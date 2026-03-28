"""FastAPI application entry point"""

from typing import Any

import uvicorn
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.agent.intent_router import IntentRouter
from src.config import settings
from src.integrations.calendar import CalendarFactory
from src.utils.logger import configure_logging, get_logger
from src.voice.retell_client import RetellAIClient
from src.voice.vapi_client import VapiAIClient
from src.webhooks.handlers import WebhookEventHandler

# Configure logging
configure_logging()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Voice Agent",
    description="Multi-provider AI voice agent for lead qualification and appointment booking",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize global components
webhook_handler = WebhookEventHandler()
intent_router = IntentRouter()
calendar = CalendarFactory.create("mock")

logger.info("AI Voice Agent initialized", version="0.1.0", env=settings.app_env)


# Pydantic models
class RetellWebhook(BaseModel):
    """Retell AI webhook payload"""

    type: str
    callId: str | None = None
    phoneNumber: str | None = None
    message: str | None = None
    timestamp: str | None = None


class VapiWebhook(BaseModel):
    """Vapi AI webhook payload"""

    type: str
    call_id: str | None = None
    phone_number: str | None = None
    transcript: str | None = None


class GHLWebhook(BaseModel):
    """GoHighLevel webhook payload"""

    event: str
    data: dict[str, Any]


class CreateCallRequest(BaseModel):
    """Request to create a voice call"""

    phone_number: str
    provider: str = "retell"  # retell or vapi
    assistant_id: str | None = None
    metadata: dict[str, Any] | None = None


class ConversationResponse(BaseModel):
    """Conversation response model"""

    conversation_id: str
    state: str
    contact: dict[str, Any]
    intent: str | None = None
    message_count: int
    metadata: dict[str, Any]


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "environment": settings.app_env,
    }


# Webhook endpoints
@app.post("/webhooks/retell")
async def retell_webhook(webhook: RetellWebhook):
    """Handle Retell AI webhooks"""
    logger.info("Received Retell webhook", event_type=webhook.type)

    try:
        result = await webhook_handler.handle_retell_webhook(webhook.dict())
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error("Failed to handle Retell webhook", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhooks/vapi")
async def vapi_webhook(webhook: VapiWebhook):
    """Handle Vapi AI webhooks"""
    logger.info("Received Vapi webhook", event_type=webhook.type)

    try:
        result = await webhook_handler.handle_vapi_webhook(webhook.dict())
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error("Failed to handle Vapi webhook", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhooks/ghl")
async def ghl_webhook(
    webhook: GHLWebhook,
    x_webhook_signature: str | None = Header(None),
):
    """Handle GoHighLevel webhooks"""
    logger.info("Received GHL webhook", event_type=webhook.event)

    try:
        result = await webhook_handler.handle_ghl_webhook(webhook.event, webhook.data)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error("Failed to handle GHL webhook", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# Voice call endpoints
@app.post("/calls/create")
async def create_call(request: CreateCallRequest):
    """Create a new voice call"""
    logger.info("Creating voice call", provider=request.provider, phone=request.phone_number)

    try:
        if request.provider == "retell":
            if not settings.retell_api_key or not settings.retell_agent_id:
                raise ValueError("Retell configuration missing")

            client = RetellAIClient()
            result = await client.create_web_call(
                agent_id=settings.retell_agent_id,
                user_phone_number=request.phone_number,
                metadata=request.metadata or {},
            )
            await client.close()

            return {
                "status": "success",
                "provider": "retell",
                "call": result,
            }

        if request.provider == "vapi":
            if not settings.vapi_api_key:
                raise ValueError("Vapi configuration missing")

            client = VapiAIClient()
            result = await client.create_call(
                phone_number=request.phone_number,
                assistant_id=request.assistant_id or "default",
                metadata=request.metadata or {},
            )
            await client.close()

            return {
                "status": "success",
                "provider": "vapi",
                "call": result,
            }
        raise ValueError(f"Unknown provider: {request.provider}")

    except Exception as e:
        logger.error("Failed to create call", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# Conversation endpoints
@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str) -> ConversationResponse:
    """Get conversation details"""
    conversation = webhook_handler.get_conversation(conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return ConversationResponse(
        conversation_id=conversation.conversation_id,
        state=conversation.state.value,
        contact={
            "name": conversation.contact.name,
            "phone": conversation.contact.phone,
            "email": conversation.contact.email,
            "company": conversation.contact.company,
        },
        intent=conversation.intent,
        message_count=len(conversation.messages),
        metadata=conversation.metadata,
    )


@app.get("/conversations/{conversation_id}/summary")
async def get_conversation_summary(conversation_id: str):
    """Get conversation summary"""
    summary = webhook_handler.get_conversation_summary(conversation_id)

    if not summary:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"status": "success", "summary": summary}


@app.post("/conversations/{conversation_id}/intent-detect")
async def detect_intent(conversation_id: str, message: str):
    """Detect intent from a message"""
    logger.info("Detecting intent", conversation_id=conversation_id)

    try:
        intent = await intent_router.detect_intent(message)
        return {
            "status": "success",
            "conversation_id": conversation_id,
            "message": message,
            "intent": intent.value,
        }
    except Exception as e:
        logger.error("Failed to detect intent", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# Calendar endpoints
@app.get("/calendar/availability")
async def check_calendar_availability(date: str, duration_minutes: int = 30):
    """Check calendar availability for a date"""
    logger.info("Checking availability", date=date, duration=duration_minutes)

    try:
        from datetime import datetime

        date_obj = datetime.fromisoformat(date)
        slots = await calendar.check_availability(date_obj, duration_minutes)

        return {
            "status": "success",
            "date": date,
            "duration_minutes": duration_minutes,
            "available_slots": [
                {
                    "start": slot["start"].isoformat(),
                    "end": slot["end"].isoformat(),
                }
                for slot in slots
            ],
        }
    except Exception as e:
        logger.error("Failed to check availability", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calendar/appointment")
async def book_appointment(
    contact_name: str,
    contact_email: str,
    start_time: str,
    duration_minutes: int = 30,
    title: str = "Consultation",
):
    """Book an appointment"""
    logger.info("Booking appointment", contact=contact_name, start_time=start_time)

    try:
        from datetime import datetime

        start_time_obj = datetime.fromisoformat(start_time)
        appointment = await calendar.book_appointment(
            contact_name=contact_name,
            contact_email=contact_email,
            start_time=start_time_obj,
            duration_minutes=duration_minutes,
            title=title,
        )

        return {
            "status": "success",
            "appointment": appointment,
        }
    except Exception as e:
        logger.error("Failed to book appointment", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# Utility endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Voice Agent API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/config")
async def get_config():
    """Get current configuration (non-sensitive)"""
    return {
        "environment": settings.app_env,
        "log_level": settings.log_level,
        "calendar_service": settings.calendar_service,
        "openai_model": settings.openai_model,
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.app_host,
        port=settings.app_port,
    )
