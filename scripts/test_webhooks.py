"""Script to test webhook endpoints"""

import httpx
import json
import asyncio
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


async def test_health_check():
    """Test health check endpoint"""
    print("\nTesting: GET /health")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")


async def test_retell_webhook():
    """Test Retell webhook"""
    print("\nTesting: POST /webhooks/retell")

    payload = {
        "type": "call_started",
        "callId": "test_retell_001",
        "phoneNumber": "+1-555-0100",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/webhooks/retell",
            json=payload,
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")


async def test_vapi_webhook():
    """Test Vapi webhook"""
    print("\nTesting: POST /webhooks/vapi")

    payload = {
        "type": "call.started",
        "call_id": "test_vapi_001",
        "phone_number": "+1-555-0200",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/webhooks/vapi",
            json=payload,
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")


async def test_ghl_webhook():
    """Test GoHighLevel webhook"""
    print("\nTesting: POST /webhooks/ghl")

    payload = {
        "event": "contact.created",
        "data": {
            "contactId": "ghl_001",
            "name": "Test User",
            "phone": "+1-555-0300",
            "email": "test@example.com",
        },
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/webhooks/ghl",
            json=payload,
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")


async def test_create_call():
    """Test create call endpoint"""
    print("\nTesting: POST /calls/create")

    payload = {
        "phone_number": "+1-555-0400",
        "provider": "retell",
        "metadata": {"source": "test"},
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/calls/create",
            json=payload,
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 500:
            print("Note: 500 error expected if API keys not configured")


async def test_detect_intent():
    """Test intent detection"""
    print("\nTesting: POST /conversations/test_001/intent-detect")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/conversations/test_001/intent-detect",
            params={"message": "I'd like to schedule an appointment"},
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")


async def test_calendar_availability():
    """Test calendar availability check"""
    print("\nTesting: GET /calendar/availability")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/calendar/availability",
            params={
                "date": "2026-04-01",
                "duration_minutes": 30,
            },
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")


async def test_all():
    """Run all webhook tests"""
    print("="*60)
    print("AI VOICE AGENT - WEBHOOK TESTS")
    print("="*60)

    try:
        await test_health_check()
        await test_retell_webhook()
        await test_vapi_webhook()
        await test_ghl_webhook()
        await test_detect_intent()
        await test_calendar_availability()
        # Skip create_call test as it requires API keys
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure the FastAPI server is running:")
        print("  uvicorn src.main:app --reload")

    print("\n" + "="*60)
    print("TESTS COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_all())
