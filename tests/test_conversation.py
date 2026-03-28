"""Tests for conversation state machine"""

import pytest

from src.agent.conversation import (
    Conversation,
    ConversationState,
    ConversationStateMachine,
)


@pytest.fixture
def conversation():
    """Create a test conversation"""
    return Conversation(conversation_id="test_001")


@pytest.fixture
def state_machine(conversation):
    """Create a test state machine"""
    return ConversationStateMachine(conversation)


def test_conversation_initialization(conversation):
    """Test conversation initialization"""
    assert conversation.conversation_id == "test_001"
    assert conversation.state == ConversationState.GREETING
    assert conversation.contact.name is None
    assert len(conversation.messages) == 0


def test_add_message(conversation):
    """Test adding messages to conversation"""
    conversation.add_message("user", "Hello")
    conversation.add_message("agent", "Hi there")

    assert len(conversation.messages) == 2
    assert conversation.messages[0]["role"] == "user"
    assert conversation.messages[0]["content"] == "Hello"
    assert conversation.messages[1]["role"] == "agent"


def test_state_transition_greeting_to_qualification(state_machine, conversation):
    """Test transition from greeting to qualification"""
    assert state_machine.can_transition(ConversationState.QUALIFICATION)
    state_machine.transition_to_qualification()
    assert conversation.state == ConversationState.QUALIFICATION


def test_state_transition_qualification_to_booking(state_machine, conversation):
    """Test transition from qualification to booking"""
    state_machine.transition_to_qualification()
    assert state_machine.can_transition(ConversationState.BOOKING)
    state_machine.transition_to_booking()
    assert conversation.state == ConversationState.BOOKING


def test_invalid_state_transition(state_machine, conversation):
    """Test invalid state transitions"""
    # From GREETING, can't go directly to BOOKING
    assert not state_machine.can_transition(ConversationState.BOOKING)


def test_conversation_end(state_machine, conversation):
    """Test ending a conversation"""
    state_machine.transition_to_farewell()
    state_machine.end_conversation()

    assert conversation.state == ConversationState.ENDED
    assert conversation.ended_at is not None


def test_contact_data(conversation):
    """Test setting contact data"""
    conversation.contact.name = "John Doe"
    conversation.contact.email = "john@example.com"
    conversation.contact.phone = "+1-555-0100"

    assert conversation.contact.name == "John Doe"
    assert conversation.contact.email == "john@example.com"


def test_conversation_to_dict(conversation, state_machine):
    """Test converting conversation to dictionary"""
    conversation.contact.name = "Jane Doe"
    conversation.intent = "schedule_appointment"
    conversation.add_message("user", "I'd like to schedule")

    conv_dict = conversation.to_dict()

    assert conv_dict["conversation_id"] == "test_001"
    assert conv_dict["state"] == "greeting"
    assert conv_dict["contact"]["name"] == "Jane Doe"
    assert conv_dict["intent"] == "schedule_appointment"
    assert conv_dict["messages_count"] == 1


def test_conversation_summary(state_machine, conversation):
    """Test getting conversation summary"""
    conversation.contact.name = "Bob Smith"
    conversation.intent = "product_info"
    conversation.add_message("user", "Tell me about your product")

    summary = state_machine.get_conversation_summary()

    assert summary["conversation_id"] == "test_001"
    assert summary["contact_name"] == "Bob Smith"
    assert summary["intent"] == "product_info"
    assert summary["message_count"] == 1
    assert summary["appointment_scheduled"] is False
