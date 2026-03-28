"""Intent detection and routing using LLM"""

from enum import Enum
from typing import Any

from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Intent(str, Enum):
    """Supported intents"""

    SCHEDULE_APPOINTMENT = "schedule_appointment"
    GENERAL_INQUIRY = "general_inquiry"
    PRODUCT_INFO = "product_info"
    SUPPORT_REQUEST = "support_request"
    CALLBACK = "callback"
    UNKNOWN = "unknown"


class IntentRouter:
    """Route user messages to appropriate intents"""

    def __init__(self):
        """Initialize intent router"""
        try:
            from openai import AsyncOpenAI

            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        except ImportError:
            logger.warning("OpenAI client not initialized, using mock routing")
            self.client = None

    async def detect_intent(self, text: str, context: dict[str, Any] | None = None) -> Intent:
        """Detect intent from user message using LLM"""
        if not self.client:
            return self._mock_intent_detection(text)

        try:
            system_prompt = """You are an intent detection system for a voice agent.
Analyze the user's message and return ONLY one of these intents:
- schedule_appointment
- general_inquiry
- product_info
- support_request
- callback
- unknown

Respond with just the intent name, nothing else."""

            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.1,
                max_tokens=10,
            )

            intent_text = response.choices[0].message.content.strip().lower()
            try:
                intent = Intent(intent_text)
            except ValueError:
                intent = Intent.UNKNOWN

            logger.info("Detected intent", intent=intent.value, text=text[:50])
            return intent

        except Exception as e:
            logger.error("Failed to detect intent", error=str(e))
            return Intent.UNKNOWN

    def _mock_intent_detection(self, text: str) -> Intent:
        """Mock intent detection for testing"""
        text_lower = text.lower()

        if any(
            word in text_lower for word in ["schedule", "book", "appointment", "meeting", "call"]
        ):
            return Intent.SCHEDULE_APPOINTMENT
        if any(word in text_lower for word in ["info", "tell", "what", "how"]):
            return Intent.PRODUCT_INFO
        if any(word in text_lower for word in ["help", "support", "issue", "problem", "broken"]):
            return Intent.SUPPORT_REQUEST
        if any(word in text_lower for word in ["callback", "call me back"]):
            return Intent.CALLBACK
        return Intent.GENERAL_INQUIRY

    async def route_conversation(self, intent: Intent, context: dict[str, Any]) -> dict[str, Any]:
        """Route conversation based on detected intent"""
        routing_map = {
            Intent.SCHEDULE_APPOINTMENT: {"next_state": "booking", "priority": "high"},
            Intent.GENERAL_INQUIRY: {"next_state": "qualification", "priority": "medium"},
            Intent.PRODUCT_INFO: {"next_state": "qualification", "priority": "medium"},
            Intent.SUPPORT_REQUEST: {"next_state": "qualification", "priority": "high"},
            Intent.CALLBACK: {"next_state": "booking", "priority": "high"},
            Intent.UNKNOWN: {"next_state": "qualification", "priority": "low"},
        }

        routing = routing_map.get(intent, routing_map[Intent.UNKNOWN])
        logger.info("Routed conversation", intent=intent.value, routing=routing)

        return {
            "intent": intent.value,
            "next_state": routing["next_state"],
            "priority": routing["priority"],
            "context": context,
        }

    async def extract_entities(
        self, text: str, entity_types: list[str] | None = None
    ) -> dict[str, Any]:
        """Extract named entities from text"""
        if not self.client:
            return self._mock_entity_extraction(text)

        try:
            entity_types = entity_types or ["name", "email", "phone", "company"]

            prompt = f"""Extract these entity types from the text: {", ".join(entity_types)}
Return as JSON with entity type as key and extracted value or null.
Example: {{"name": "John", "email": "john@example.com", "phone": null, "company": "Acme"}}

Text: {text}"""

            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200,
            )

            import json

            entities = json.loads(response.choices[0].message.content)
            logger.info("Extracted entities", entities=entities)
            return entities

        except Exception as e:
            logger.error("Failed to extract entities", error=str(e))
            return dict.fromkeys(entity_types or [])

    def _mock_entity_extraction(self, text: str) -> dict[str, Any]:
        """Mock entity extraction for testing"""
        return {
            "name": None,
            "email": None,
            "phone": None,
            "company": None,
        }
