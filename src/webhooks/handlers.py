"""Webhook event handlers"""

from typing import Any

from src.agent.conversation import Conversation, ConversationStateMachine
from src.integrations.airtable_sync import AirtableSyncClient
from src.integrations.ghl_webhook import GoHighLevelWebhookHandler
from src.utils.logger import get_logger

logger = get_logger(__name__)


class WebhookEventHandler:
    """Handle webhook events from various sources"""

    def __init__(self):
        """Initialize webhook event handler"""
        self.ghl_webhook_handler = GoHighLevelWebhookHandler()
        self.conversations: dict[str, Conversation] = {}

    async def handle_retell_webhook(self, event: dict[str, Any]) -> dict[str, Any]:
        """Handle Retell AI webhook event"""
        event_type = event.get("type")
        logger.info("Processing Retell webhook", event_type=event_type)

        if event_type == "call_started":
            return await self._handle_call_started(event)
        if event_type == "call_ended":
            return await self._handle_call_ended(event)
        if event_type == "transcript":
            return await self._handle_transcript(event)
        logger.warning("Unknown Retell event type", event_type=event_type)
        return {"status": "ignored", "event_type": event_type}

    async def handle_vapi_webhook(self, event: dict[str, Any]) -> dict[str, Any]:
        """Handle Vapi AI webhook event"""
        event_type = event.get("type")
        logger.info("Processing Vapi webhook", event_type=event_type)

        if event_type == "call.started":
            return await self._handle_call_started(event)
        if event_type == "call.ended":
            return await self._handle_call_ended(event)
        if event_type == "call.transcript_update":
            return await self._handle_transcript(event)
        logger.warning("Unknown Vapi event type", event_type=event_type)
        return {"status": "ignored", "event_type": event_type}

    async def handle_ghl_webhook(self, event_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Handle GoHighLevel webhook event"""
        logger.info("Processing GHL webhook", event_type=event_type)

        parsed_event = self.ghl_webhook_handler.parse_webhook_event(event_type, data)
        action = parsed_event.get("action")

        if action == "contact_created":
            return await self._handle_contact_created(parsed_event)
        if action == "appointment_scheduled":
            return await self._handle_appointment_scheduled(parsed_event)
        logger.warning("Unknown GHL action", action=action)
        return {"status": "processed", "action": action}

    async def _handle_call_started(self, event: dict[str, Any]) -> dict[str, Any]:
        """Handle call started event"""
        call_id = event.get("callId") or event.get("call_id")
        phone_number = event.get("phoneNumber") or event.get("phone_number")

        logger.info("Call started", call_id=call_id, phone_number=phone_number)

        # Create conversation
        conversation = Conversation(conversation_id=call_id)
        conversation.contact.phone = phone_number
        conversation.metadata["source"] = event.get("source", "unknown")

        self.conversations[call_id] = conversation
        state_machine = ConversationStateMachine(conversation)
        state_machine.transition_to_greeting()

        return {
            "status": "processed",
            "conversation_id": call_id,
            "state": "greeting",
        }

    async def _handle_call_ended(self, event: dict[str, Any]) -> dict[str, Any]:
        """Handle call ended event"""
        call_id = event.get("callId") or event.get("call_id")
        logger.info("Call ended", call_id=call_id)

        if call_id in self.conversations:
            conversation = self.conversations[call_id]
            state_machine = ConversationStateMachine(conversation)
            state_machine.end_conversation()

            # Sync to Airtable
            try:
                airtable = AirtableSyncClient()
                call_data = {
                    "Call ID": call_id,
                    "Contact Name": conversation.contact.name,
                    "Contact Phone": conversation.contact.phone,
                    "Contact Email": conversation.contact.email,
                    "Intent": conversation.intent or "unknown",
                    "Duration": (conversation.ended_at - conversation.started_at).total_seconds()
                    if conversation.ended_at
                    else 0,
                    "Status": conversation.state.value,
                    "Message Count": len(conversation.messages),
                }
                await airtable.create_call_record(call_data)
                await airtable.close()
            except Exception as e:
                logger.error("Failed to sync call to Airtable", error=str(e))

        return {
            "status": "processed",
            "conversation_id": call_id,
            "state": "ended",
        }

    async def _handle_transcript(self, event: dict[str, Any]) -> dict[str, Any]:
        """Handle transcript/message event"""
        call_id = event.get("callId") or event.get("call_id")
        message = event.get("message") or event.get("transcript")
        role = event.get("role", "user")

        logger.info("Transcript received", call_id=call_id, role=role)

        if call_id in self.conversations:
            conversation = self.conversations[call_id]
            conversation.add_message(role, message)

        return {
            "status": "processed",
            "conversation_id": call_id,
            "message_logged": True,
        }

    async def _handle_contact_created(self, event: dict[str, Any]) -> dict[str, Any]:
        """Handle contact created event from GHL"""
        logger.info("Contact created from GHL", contact_id=event.get("contact_id"))

        try:
            airtable = AirtableSyncClient()
            lead_data = {
                "Name": event.get("contact_name", ""),
                "Phone": event.get("phone", ""),
                "Email": event.get("email", ""),
                "Source": "GoHighLevel",
                "Status": "New Lead",
            }
            await airtable.create_lead(lead_data)
            await airtable.close()
            logger.info("Lead synced to Airtable")
        except Exception as e:
            logger.error("Failed to sync lead to Airtable", error=str(e))

        return {
            "status": "processed",
            "action": "contact_created",
            "contact_id": event.get("contact_id"),
        }

    async def _handle_appointment_scheduled(self, event: dict[str, Any]) -> dict[str, Any]:
        """Handle appointment scheduled event"""
        logger.info(
            "Appointment scheduled",
            appointment_id=event.get("appointment_id"),
            contact_id=event.get("contact_id"),
        )

        return {
            "status": "processed",
            "action": "appointment_scheduled",
            "appointment_id": event.get("appointment_id"),
        }

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        """Get conversation by ID"""
        return self.conversations.get(conversation_id)

    def get_conversation_summary(self, conversation_id: str) -> dict[str, Any] | None:
        """Get conversation summary"""
        conversation = self.get_conversation(conversation_id)
        if conversation:
            state_machine = ConversationStateMachine(conversation)
            return state_machine.get_conversation_summary()
        return None
