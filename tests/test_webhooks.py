"""Tests for webhook handlers"""

import pytest

from src.webhooks.handlers import WebhookEventHandler


@pytest.fixture
def webhook_handler():
    """Create a test webhook handler"""
    return WebhookEventHandler()


@pytest.mark.asyncio
async def test_handle_retell_call_started(webhook_handler):
    """Test handling Retell call started event"""
    event = {
        "type": "call_started",
        "callId": "call_123",
        "phoneNumber": "+1-555-0100",
    }

    result = await webhook_handler.handle_retell_webhook(event)

    assert result["status"] == "processed"
    assert result["conversation_id"] == "call_123"
    assert result["state"] == "greeting"


@pytest.mark.asyncio
async def test_handle_retell_transcript(webhook_handler):
    """Test handling Retell transcript event"""
    # First create a call
    event_started = {
        "type": "call_started",
        "callId": "call_456",
        "phoneNumber": "+1-555-0200",
    }
    await webhook_handler.handle_retell_webhook(event_started)

    # Then add a transcript
    event_transcript = {
        "type": "transcript",
        "callId": "call_456",
        "message": "Hello, I'd like to schedule",
        "role": "user",
    }

    result = await webhook_handler.handle_retell_webhook(event_transcript)

    assert result["status"] == "processed"
    assert result["message_logged"] is True

    # Verify message was added
    conversation = webhook_handler.get_conversation("call_456")
    assert len(conversation.messages) == 1
    assert conversation.messages[0]["content"] == "Hello, I'd like to schedule"


@pytest.mark.asyncio
async def test_handle_retell_call_ended(webhook_handler):
    """Test handling Retell call ended event"""
    # First create a call
    event_started = {
        "type": "call_started",
        "callId": "call_789",
        "phoneNumber": "+1-555-0300",
    }
    await webhook_handler.handle_retell_webhook(event_started)

    # Then end it
    event_ended = {
        "type": "call_ended",
        "callId": "call_789",
    }

    result = await webhook_handler.handle_retell_webhook(event_ended)

    assert result["status"] == "processed"
    assert result["state"] == "ended"

    # Verify conversation is ended
    conversation = webhook_handler.get_conversation("call_789")
    assert conversation.state.value == "ended"
    assert conversation.ended_at is not None


@pytest.mark.asyncio
async def test_handle_vapi_call_started(webhook_handler):
    """Test handling Vapi call started event"""
    event = {
        "type": "call.started",
        "call_id": "vapi_call_001",
        "phone_number": "+1-555-0400",
    }

    result = await webhook_handler.handle_vapi_webhook(event)

    assert result["status"] == "processed"
    assert result["conversation_id"] == "vapi_call_001"


@pytest.mark.asyncio
async def test_handle_ghl_contact_created(webhook_handler):
    """Test handling GHL contact created event"""
    result = await webhook_handler.handle_ghl_webhook(
        "contact.created",
        {
            "contactId": "ghl_contact_123",
            "name": "Jane Doe",
            "phone": "+1-555-0500",
            "email": "jane@example.com",
        },
    )

    assert result["status"] == "processed"
    assert result["action"] == "contact_created"


@pytest.mark.asyncio
async def test_handle_ghl_appointment_scheduled(webhook_handler):
    """Test handling GHL appointment scheduled event"""
    result = await webhook_handler.handle_ghl_webhook(
        "appointment.scheduled",
        {
            "appointmentId": "appt_001",
            "contactId": "ghl_contact_123",
            "dateTime": "2026-04-01T10:00:00",
            "title": "Consultation",
        },
    )

    assert result["status"] == "processed"
    assert result["action"] == "appointment_scheduled"


def test_get_conversation_not_found(webhook_handler):
    """Test getting non-existent conversation"""
    conversation = webhook_handler.get_conversation("nonexistent")
    assert conversation is None


@pytest.mark.asyncio
async def test_get_conversation_summary(webhook_handler):
    """Test getting conversation summary"""
    # Create a conversation
    event = {
        "type": "call_started",
        "callId": "call_summary_test",
        "phoneNumber": "+1-555-0600",
    }
    await webhook_handler.handle_retell_webhook(event)

    # Get summary
    summary = webhook_handler.get_conversation_summary("call_summary_test")

    assert summary is not None
    assert summary["conversation_id"] == "call_summary_test"
    assert summary["state"] == "greeting"
