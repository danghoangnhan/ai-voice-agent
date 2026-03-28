"""Script to simulate a voice call flow"""

import asyncio

from src.agent.intent_router import IntentRouter
from src.utils.logger import configure_logging, get_logger
from src.webhooks.handlers import WebhookEventHandler

configure_logging()
logger = get_logger(__name__)


async def simulate_call():
    """Simulate a complete voice call flow"""

    webhook_handler = WebhookEventHandler()
    intent_router = IntentRouter()

    call_id = "sim_call_001"
    phone_number = "+1-555-0123"

    print("\n" + "=" * 60)
    print("AI VOICE AGENT - CALL SIMULATION")
    print("=" * 60 + "\n")

    # 1. Call started
    print("1. CALL STARTED")
    print(f"   Call ID: {call_id}")
    print(f"   From: {phone_number}\n")

    call_started_event = {
        "type": "call_started",
        "callId": call_id,
        "phoneNumber": phone_number,
    }

    result = await webhook_handler.handle_retell_webhook(call_started_event)
    print(f"   Status: {result['status']}")
    print(f"   State: {result['state']}\n")

    # 2. Greeting message from agent
    print("2. AGENT GREETING")
    print("   Agent: Hi there! Thanks for giving us a call.")
    print("   Agent: This is Sarah from our team. How can I help you today?\n")

    # 3. User responds
    print("3. USER RESPONSE")
    user_message = "Hi Sarah, I'd like to schedule a call with your sales team"
    print(f"   User: {user_message}\n")

    # Add transcript event
    transcript_event = {
        "type": "transcript",
        "callId": call_id,
        "message": user_message,
        "role": "user",
    }

    await webhook_handler.handle_retell_webhook(transcript_event)

    # 4. Detect intent
    print("4. INTENT DETECTION")
    intent = await intent_router.detect_intent(user_message)
    print(f"   Detected Intent: {intent.value}\n")

    conversation = webhook_handler.get_conversation(call_id)
    conversation.intent = intent.value

    # Route conversation
    routing = await intent_router.route_conversation(intent, {})
    print(f"   Next State: {routing['next_state']}")
    print(f"   Priority: {routing['priority']}\n")

    # 5. Qualification phase
    print("5. QUALIFICATION PHASE")
    print("   Agent: That's great! I can help with that.")
    print("   Agent: To better assist you, can you tell me your name?\n")

    user_name_msg = "My name is John Smith"
    print(f"   User: {user_name_msg}\n")

    # Extract entities
    print("6. ENTITY EXTRACTION")
    entities = await intent_router.extract_entities(f"{user_message} {user_name_msg}")
    print(f"   Extracted Name: {entities.get('name', 'N/A')}")
    print(f"   Extracted Email: {entities.get('email', 'N/A')}")
    print(f"   Extracted Phone: {entities.get('phone', 'N/A')}\n")

    # Update conversation
    if entities.get("name"):
        conversation.contact.name = entities["name"]
    else:
        conversation.contact.name = "John Smith"

    # 7. Booking phase
    print("7. APPOINTMENT BOOKING")
    print("   Agent: Perfect, John! Let me get you scheduled.")
    print("   Agent: What day works best for you this week?\n")

    user_availability = "How about Thursday at 2 PM?"
    print(f"   User: {user_availability}\n")

    # 8. Confirmation
    print("8. APPOINTMENT CONFIRMATION")
    print("   Agent: Great! I've scheduled you for Thursday at 2 PM.")
    print("   Agent: You'll receive a calendar invite shortly.\n")

    # 9. Farewell
    print("9. FAREWELL")
    print("   Agent: Thanks for your time, John. Looking forward to speaking with you!\n")

    # 10. Call ended
    print("10. CALL ENDED")
    call_ended_event = {
        "type": "call_ended",
        "callId": call_id,
    }

    result = await webhook_handler.handle_retell_webhook(call_ended_event)
    print(f"    Status: {result['status']}")
    print(f"    State: {result['state']}\n")

    # Get conversation summary
    print("11. CONVERSATION SUMMARY")
    summary = webhook_handler.get_conversation_summary(call_id)
    print(f"    Conversation ID: {summary['conversation_id']}")
    print(f"    Contact Name: {summary['contact_name']}")
    print(f"    Intent: {summary['intent']}")
    print(f"    Appointment Scheduled: {summary['appointment_scheduled']}")
    print(f"    Messages: {summary['message_count']}")
    print(f"    Duration: {summary['duration_seconds']:.1f} seconds\n")

    print("=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(simulate_call())
