"""GoHighLevel webhook handler and API client"""

import hashlib
import hmac
from typing import Any

import httpx

from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GoHighLevelWebhookHandler:
    """Handler for GoHighLevel webhooks"""

    def __init__(self, webhook_secret: str | None = None):
        """Initialize webhook handler"""
        self.webhook_secret = webhook_secret or settings.ghl_webhook_secret

    def verify_signature(self, payload: str, signature: str) -> bool:
        """Verify webhook signature"""
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured, skipping verification")
            return True

        try:
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                payload.encode(),
                hashlib.sha256,
            ).hexdigest()

            is_valid = hmac.compare_digest(expected_signature, signature)
            if not is_valid:
                logger.warning("Invalid webhook signature")
            return is_valid

        except Exception as e:
            logger.error("Failed to verify webhook signature", error=str(e))
            return False

    def parse_webhook_event(self, event_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Parse and process webhook event"""
        logger.info("Processing GHL webhook", event_type=event_type)

        if event_type == "contact.created":
            return self._handle_contact_created(data)
        if event_type == "contact.updated":
            return self._handle_contact_updated(data)
        if event_type == "appointment.scheduled":
            return self._handle_appointment_scheduled(data)
        if event_type == "conversation.message":
            return self._handle_conversation_message(data)
        logger.warning("Unknown webhook event type", event_type=event_type)
        return {"event_type": event_type, "data": data}

    def _handle_contact_created(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle contact created event"""
        logger.info("Contact created", contact_id=data.get("contactId"))
        return {
            "action": "contact_created",
            "contact_id": data.get("contactId"),
            "contact_name": data.get("name"),
            "phone": data.get("phone"),
            "email": data.get("email"),
        }

    def _handle_contact_updated(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle contact updated event"""
        logger.info("Contact updated", contact_id=data.get("contactId"))
        return {
            "action": "contact_updated",
            "contact_id": data.get("contactId"),
            "updates": data.get("updates", {}),
        }

    def _handle_appointment_scheduled(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle appointment scheduled event"""
        logger.info("Appointment scheduled", appointment_id=data.get("appointmentId"))
        return {
            "action": "appointment_scheduled",
            "appointment_id": data.get("appointmentId"),
            "contact_id": data.get("contactId"),
            "date_time": data.get("dateTime"),
            "title": data.get("title"),
        }

    def _handle_conversation_message(self, data: dict[str, Any]) -> dict[str, Any]:
        """Handle conversation message event"""
        logger.info("Conversation message", conversation_id=data.get("conversationId"))
        return {
            "action": "conversation_message",
            "conversation_id": data.get("conversationId"),
            "contact_id": data.get("contactId"),
            "message": data.get("message"),
        }


class GoHighLevelAPIClient:
    """Client for GoHighLevel API"""

    BASE_URL = "https://api.gohighlevel.com/v1"

    def __init__(self, api_key: str | None = None, account_id: str | None = None):
        """Initialize GHL API client"""
        self.api_key = api_key or settings.ghl_api_key
        self.account_id = account_id or settings.ghl_account_id

        if not self.api_key or not self.account_id:
            raise ValueError("GHL_API_KEY and GHL_ACCOUNT_ID must be configured")

        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def create_contact(self, contact_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new contact"""
        payload = {
            "firstName": contact_data.get("first_name", ""),
            "lastName": contact_data.get("last_name", ""),
            "email": contact_data.get("email"),
            "phone": contact_data.get("phone"),
            "companyName": contact_data.get("company"),
        }

        try:
            response = await self.client.post(
                f"/contacts/?accountId={self.account_id}",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            logger.info("Created GHL contact", contact_id=result.get("id"))
            return result
        except httpx.HTTPError as e:
            logger.error("Failed to create GHL contact", error=str(e))
            raise

    async def update_contact(self, contact_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update a contact"""
        payload = {
            "firstName": updates.get("first_name"),
            "lastName": updates.get("last_name"),
            "email": updates.get("email"),
            "phone": updates.get("phone"),
            "companyName": updates.get("company"),
        }

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        try:
            response = await self.client.put(
                f"/contacts/{contact_id}?accountId={self.account_id}",
                json=payload,
            )
            response.raise_for_status()
            logger.info("Updated GHL contact", contact_id=contact_id)
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to update GHL contact", error=str(e))
            raise

    async def get_contact(self, contact_id: str) -> dict[str, Any]:
        """Get contact details"""
        try:
            response = await self.client.get(f"/contacts/{contact_id}?accountId={self.account_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to get GHL contact", error=str(e))
            raise

    async def schedule_appointment(self, appointment_data: dict[str, Any]) -> dict[str, Any]:
        """Schedule an appointment"""
        payload = {
            "contactId": appointment_data.get("contact_id"),
            "title": appointment_data.get("title"),
            "startDate": appointment_data.get("start_date"),
            "endDate": appointment_data.get("end_date"),
            "location": appointment_data.get("location"),
            "description": appointment_data.get("description"),
        }

        try:
            response = await self.client.post(
                f"/appointments/?accountId={self.account_id}",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            logger.info("Scheduled GHL appointment", appointment_id=result.get("id"))
            return result
        except httpx.HTTPError as e:
            logger.error("Failed to schedule GHL appointment", error=str(e))
            raise

    async def close(self):
        """Close the client connection"""
        await self.client.aclose()
