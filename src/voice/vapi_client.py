"""Vapi AI API client wrapper"""

import httpx
from typing import Optional, Dict, Any, List
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VapiAIClient:
    """Client for Vapi AI voice agent API"""

    BASE_URL = "https://api.vapi.ai"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Vapi AI client"""
        self.api_key = api_key or settings.vapi_api_key
        if not self.api_key:
            raise ValueError("VAPI_API_KEY not configured")

        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def create_call(
        self,
        phone_number: str,
        assistant_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create an outbound phone call"""
        payload = {
            "phoneNumber": phone_number,
            "assistantId": assistant_id,
            "metadata": metadata or {},
        }

        try:
            response = await self.client.post("/call/phone", json=payload)
            response.raise_for_status()
            logger.info("Created Vapi phone call", phone_number=phone_number)
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to create Vapi phone call", error=str(e))
            raise

    async def get_call(self, call_id: str) -> Dict[str, Any]:
        """Get call details"""
        try:
            response = await self.client.get(f"/call/{call_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to get Vapi call", call_id=call_id, error=str(e))
            raise

    async def list_calls(
        self, limit: int = 10, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List recent calls"""
        try:
            response = await self.client.get(
                "/call", params={"limit": limit, "offset": offset}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to list Vapi calls", error=str(e))
            raise

    async def end_call(self, call_id: str) -> Dict[str, Any]:
        """End an active call"""
        try:
            response = await self.client.post(f"/call/{call_id}/end")
            response.raise_for_status()
            logger.info("Ended Vapi call", call_id=call_id)
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to end Vapi call", error=str(e))
            raise

    async def update_assistant(
        self, assistant_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update assistant configuration"""
        try:
            response = await self.client.patch(f"/assistant/{assistant_id}", json=updates)
            response.raise_for_status()
            logger.info("Updated Vapi assistant", assistant_id=assistant_id)
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to update Vapi assistant", error=str(e))
            raise

    async def get_assistant(self, assistant_id: str) -> Dict[str, Any]:
        """Get assistant configuration"""
        try:
            response = await self.client.get(f"/assistant/{assistant_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to get Vapi assistant", error=str(e))
            raise

    async def close(self):
        """Close the client connection"""
        await self.client.aclose()
