"""Airtable CRM synchronization"""

import httpx
from typing import Optional, Dict, Any, List
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AirtableSyncClient:
    """Client for syncing data to Airtable"""

    BASE_URL = "https://api.airtable.com/v0"

    def __init__(self, api_key: Optional[str] = None, base_id: Optional[str] = None):
        """Initialize Airtable client"""
        self.api_key = api_key or settings.airtable_api_key
        self.base_id = base_id or settings.airtable_base_id

        if not self.api_key or not self.base_id:
            raise ValueError("AIRTABLE_API_KEY and AIRTABLE_BASE_ID must be configured")

        self.client = httpx.AsyncClient(
            base_url=f"{self.BASE_URL}/{self.base_id}",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30.0,
        )

    async def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new lead record"""
        table_name = settings.airtable_leads_table

        payload = {
            "records": [
                {
                    "fields": lead_data,
                }
            ]
        }

        try:
            response = await self.client.post(f"/{table_name}", json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info("Created Airtable lead", lead_id=result["records"][0]["id"])
            return result["records"][0]
        except httpx.HTTPError as e:
            logger.error("Failed to create Airtable lead", error=str(e))
            raise

    async def update_lead(self, lead_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing lead record"""
        table_name = settings.airtable_leads_table

        payload = {
            "records": [
                {
                    "id": lead_id,
                    "fields": updates,
                }
            ]
        }

        try:
            response = await self.client.patch(f"/{table_name}", json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info("Updated Airtable lead", lead_id=lead_id)
            return result["records"][0]
        except httpx.HTTPError as e:
            logger.error("Failed to update Airtable lead", error=str(e))
            raise

    async def get_lead(self, lead_id: str) -> Dict[str, Any]:
        """Get a lead record"""
        table_name = settings.airtable_leads_table

        try:
            response = await self.client.get(f"/{table_name}/{lead_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to get Airtable lead", error=str(e))
            raise

    async def create_call_record(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a call record"""
        table_name = settings.airtable_calls_table

        payload = {
            "records": [
                {
                    "fields": call_data,
                }
            ]
        }

        try:
            response = await self.client.post(f"/{table_name}", json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info("Created Airtable call record", call_id=result["records"][0]["id"])
            return result["records"][0]
        except httpx.HTTPError as e:
            logger.error("Failed to create Airtable call record", error=str(e))
            raise

    async def update_call_record(self, call_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a call record"""
        table_name = settings.airtable_calls_table

        payload = {
            "records": [
                {
                    "id": call_id,
                    "fields": updates,
                }
            ]
        }

        try:
            response = await self.client.patch(f"/{table_name}", json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info("Updated Airtable call record", call_id=call_id)
            return result["records"][0]
        except httpx.HTTPError as e:
            logger.error("Failed to update Airtable call record", error=str(e))
            raise

    async def list_leads(self, filters: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all leads, optionally filtered"""
        table_name = settings.airtable_leads_table

        params = {}
        if filters:
            params["filterByFormula"] = filters

        try:
            response = await self.client.get(f"/{table_name}", params=params)
            response.raise_for_status()
            return response.json()["records"]
        except httpx.HTTPError as e:
            logger.error("Failed to list Airtable leads", error=str(e))
            raise

    async def close(self):
        """Close the client connection"""
        await self.client.aclose()
