"""Tests for intent detection and routing"""

import pytest

from src.agent.intent_router import Intent, IntentRouter


@pytest.fixture
def intent_router():
    """Create a test intent router"""
    return IntentRouter()


@pytest.mark.asyncio
async def test_mock_intent_schedule_appointment(intent_router):
    """Test intent detection for scheduling"""
    intent = await intent_router.detect_intent("I'd like to schedule an appointment")
    assert intent == Intent.SCHEDULE_APPOINTMENT


@pytest.mark.asyncio
async def test_mock_intent_product_info(intent_router):
    """Test intent detection for product info"""
    intent = await intent_router.detect_intent("Tell me about your features")
    assert intent == Intent.PRODUCT_INFO


@pytest.mark.asyncio
async def test_mock_intent_support_request(intent_router):
    """Test intent detection for support"""
    intent = await intent_router.detect_intent("I have a problem with my account")
    assert intent == Intent.SUPPORT_REQUEST


@pytest.mark.asyncio
async def test_mock_intent_callback(intent_router):
    """Test intent detection for callback"""
    intent = await intent_router.detect_intent("Can you call me back?")
    assert intent == Intent.CALLBACK


@pytest.mark.asyncio
async def test_mock_intent_general_inquiry(intent_router):
    """Test intent detection for general inquiry"""
    intent = await intent_router.detect_intent("Hello, just browsing")
    assert intent == Intent.GENERAL_INQUIRY


@pytest.mark.asyncio
async def test_route_conversation_schedule_appointment(intent_router):
    """Test conversation routing for appointment"""
    routing = await intent_router.route_conversation(Intent.SCHEDULE_APPOINTMENT, {"user": "test"})

    assert routing["intent"] == "schedule_appointment"
    assert routing["next_state"] == "booking"
    assert routing["priority"] == "high"


@pytest.mark.asyncio
async def test_route_conversation_product_info(intent_router):
    """Test conversation routing for product info"""
    routing = await intent_router.route_conversation(Intent.PRODUCT_INFO, {})

    assert routing["intent"] == "product_info"
    assert routing["next_state"] == "qualification"
    assert routing["priority"] == "medium"


@pytest.mark.asyncio
async def test_extract_entities(intent_router):
    """Test entity extraction"""
    entities = await intent_router.extract_entities(
        "My name is John Smith and my email is john@example.com"
    )

    assert "name" in entities
    assert "email" in entities


@pytest.mark.asyncio
async def test_detect_intent_empty_message(intent_router):
    """Test intent detection with empty message"""
    intent = await intent_router.detect_intent("")
    assert intent in [Intent.GENERAL_INQUIRY, Intent.UNKNOWN]
