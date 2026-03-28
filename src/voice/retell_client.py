"""Retell AI API client wrapper"""

from typing import Any

import httpx

from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RetellAIClient:
    """Client for Retell AI voice agent API"""

    BASE_URL = "https://api.retellai.com/v2"

    def __init__(self, api_key: str | None = None):
        """Initialize Retell AI client"""
        self.api_key = api_key or settings.retell_api_key
        if not self.api_key:
            raise ValueError("RETELL_API_KEY not configured")

        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30.0,
        )

    async def create_web_call(
        self,
        agent_id: str,
        user_phone_number: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new web call"""
        payload = {
            "agent_id": agent_id,
            "metadata": metadata or {},
        }
        if user_phone_number:
            payload["user_phone_number"] = user_phone_number

        try:
            response = await self.client.post("/call/web", json=payload)
            response.raise_for_status()
            logger.info("Created Retell web call", agent_id=agent_id)
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to create Retell web call", error=str(e))
            raise

    async def get_call(self, call_id: str) -> dict[str, Any]:
        """Get call details"""
        try:
            response = await self.client.get(f"/call/{call_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to get Retell call", call_id=call_id, error=str(e))
            raise

    async def list_calls(self, limit: int = 10, offset: int = 0) -> dict[str, Any]:
        """List recent calls"""
        try:
            response = await self.client.get("/call", params={"limit": limit, "offset": offset})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to list Retell calls", error=str(e))
            raise

    async def update_agent(self, agent_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update agent configuration"""
        try:
            response = await self.client.patch(f"/agent/{agent_id}", json=updates)
            response.raise_for_status()
            logger.info("Updated Retell agent", agent_id=agent_id)
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to update Retell agent", error=str(e))
            raise

    async def close(self):
        """Close the client connection"""
        await self.client.aclose()
