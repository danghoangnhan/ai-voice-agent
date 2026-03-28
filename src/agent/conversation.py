"""Conversation state machine for voice agent"""

from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ConversationState(str, Enum):
    """Conversation state enumeration"""
    GREETING = "greeting"
    QUALIFICATION = "qualification"
    BOOKING = "booking"
    FAREWELL = "farewell"
    ENDED = "ended"


@dataclass
class Contact:
    """Contact information"""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None


@dataclass
class Conversation:
    """Conversation state and data"""
    conversation_id: str
    state: ConversationState = ConversationState.GREETING
    contact: Contact = field(default_factory=Contact)
    intent: Optional[str] = None
    qualification_data: Dict[str, Any] = field(default_factory=dict)
    appointment: Optional[Dict[str, Any]] = None
    messages: List[Dict[str, str]] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary"""
        return {
            "conversation_id": self.conversation_id,
            "state": self.state.value,
            "contact": {
                "name": self.contact.name,
                "phone": self.contact.phone,
                "email": self.contact.email,
                "company": self.contact.company,
            },
            "intent": self.intent,
            "qualification_data": self.qualification_data,
            "appointment": self.appointment,
            "messages_count": len(self.messages),
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "metadata": self.metadata,
        }


class ConversationStateMachine:
    """State machine for managing conversation flow"""

    def __init__(self, conversation: Conversation):
        """Initialize state machine"""
        self.conversation = conversation

    def transition_to_greeting(self):
        """Transition to greeting state"""
        self.conversation.state = ConversationState.GREETING
        logger.info("Transitioned to GREETING", conversation_id=self.conversation.conversation_id)

    def transition_to_qualification(self):
        """Transition to qualification state"""
        self.conversation.state = ConversationState.QUALIFICATION
        logger.info("Transitioned to QUALIFICATION", conversation_id=self.conversation.conversation_id)

    def transition_to_booking(self):
        """Transition to booking state"""
        self.conversation.state = ConversationState.BOOKING
        logger.info("Transitioned to BOOKING", conversation_id=self.conversation.conversation_id)

    def transition_to_farewell(self):
        """Transition to farewell state"""
        self.conversation.state = ConversationState.FAREWELL
        logger.info("Transitioned to FAREWELL", conversation_id=self.conversation.conversation_id)

    def end_conversation(self):
        """End the conversation"""
        self.conversation.state = ConversationState.ENDED
        self.conversation.ended_at = datetime.utcnow()
        logger.info("Conversation ended", conversation_id=self.conversation.conversation_id)

    def can_transition(self, target_state: ConversationState) -> bool:
        """Check if transition is allowed"""
        current = self.conversation.state
        allowed_transitions = {
            ConversationState.GREETING: [ConversationState.QUALIFICATION, ConversationState.FAREWELL],
            ConversationState.QUALIFICATION: [ConversationState.BOOKING, ConversationState.FAREWELL],
            ConversationState.BOOKING: [ConversationState.FAREWELL, ConversationState.ENDED],
            ConversationState.FAREWELL: [ConversationState.ENDED],
            ConversationState.ENDED: [],
        }
        return target_state in allowed_transitions.get(current, [])

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation summary"""
        duration = None
        if self.conversation.ended_at:
            duration = (self.conversation.ended_at - self.conversation.started_at).total_seconds()

        return {
            "conversation_id": self.conversation.conversation_id,
            "state": self.conversation.state.value,
            "contact_name": self.conversation.contact.name,
            "intent": self.conversation.intent,
            "appointment_scheduled": self.conversation.appointment is not None,
            "message_count": len(self.conversation.messages),
            "duration_seconds": duration,
            "metadata": self.conversation.metadata,
        }
