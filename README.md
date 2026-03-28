# AI Voice Agent - POC

A production-ready proof-of-concept for an intelligent voice agent that handles lead qualification, appointment booking, and customer engagement. Built with support for multiple voice providers (Retell AI, Vapi AI) and CRM integrations (GoHighLevel, Airtable).

## Features

- **Multi-Provider Voice Integration**
  - Retell AI support for web-based calls
  - Vapi AI support for phone calls
  - Extensible architecture for additional providers

- **Intelligent Conversation Management**
  - State machine-based conversation flow (greeting → qualification → booking → farewell)
  - Intent detection using LLM
  - Named entity extraction
  - Knowledge base with RAG support

- **Lead Management & CRM Integration**
  - Real-time synchronization with Airtable
  - GoHighLevel webhook integration
  - Automatic lead creation and qualification tracking
  - Call recording and transcript management

- **Appointment Booking**
  - Calendar availability checking
  - Appointment scheduling with confirmation
  - Multi-provider calendar support (Google Calendar, Outlook, Custom)
  - Automated reminder and follow-up emails

- **Enterprise Features**
  - Scalable FastAPI architecture
  - Docker containerization
  - Comprehensive logging and monitoring
  - Webhook signature verification
  - Error handling and retry logic

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional)
- API keys for:
  - Retell AI (optional)
  - Vapi AI (optional)
  - OpenAI (for intent detection)
  - Airtable (for CRM sync)
  - GoHighLevel (for webhook integration)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-voice-agent
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Run the application:
```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

### Docker Setup

Run with Docker Compose:
```bash
docker-compose up --build
```

The application will be available at `http://localhost:8000`

## Project Structure

```
ai-voice-agent/
├── src/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── voice/
│   │   ├── retell_client.py    # Retell AI integration
│   │   ├── vapi_client.py      # Vapi AI integration
│   │   └── tts_engine.py       # Text-to-speech abstraction
│   ├── agent/
│   │   ├── conversation.py     # Conversation state machine
│   │   ├── intent_router.py    # Intent detection and routing
│   │   └── knowledge_base.py   # Knowledge base & RAG
│   ├── integrations/
│   │   ├── airtable_sync.py    # Airtable CRM sync
│   │   ├── ghl_webhook.py      # GoHighLevel integration
│   │   └── calendar.py         # Calendar booking
│   ├── webhooks/
│   │   └── handlers.py         # Webhook event handlers
│   └── utils/
│       └── logger.py           # Logging configuration
├── configs/
│   ├── agent_persona.yaml      # Agent personality config
│   └── routing_rules.yaml      # Call routing rules
├── templates/
│   ├── greeting.txt
│   ├── qualification.txt
│   └── appointment_booking.txt
├── tests/
│   ├── test_conversation.py
│   ├── test_intent_router.py
│   └── test_webhooks.py
└── scripts/
    ├── simulate_call.py        # Call flow simulation
    └── test_webhooks.py        # Webhook testing script
```

## API Endpoints

### Health Check
- `GET /health` - Application health status
- `GET /` - Root endpoint with documentation links

### Voice Calls
- `POST /calls/create` - Create a new voice call
- `GET /conversations/{conversation_id}` - Get conversation details
- `GET /conversations/{conversation_id}/summary` - Get conversation summary

### Webhooks
- `POST /webhooks/retell` - Retell AI webhook endpoint
- `POST /webhooks/vapi` - Vapi AI webhook endpoint
- `POST /webhooks/ghl` - GoHighLevel webhook endpoint

### Intent & Routing
- `POST /conversations/{conversation_id}/intent-detect` - Detect intent from message

### Calendar
- `GET /calendar/availability` - Check calendar availability
- `POST /calendar/appointment` - Book an appointment

## Usage Examples

### Create a Voice Call (Retell)

```bash
curl -X POST http://localhost:8000/calls/create \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1-555-0123",
    "provider": "retell",
    "metadata": {"source": "api"}
  }'
```

### Detect Intent

```bash
curl -X POST "http://localhost:8000/conversations/conv_001/intent-detect?message=I%27d%20like%20to%20schedule%20an%20appointment"
```

### Check Calendar Availability

```bash
curl -X GET "http://localhost:8000/calendar/availability?date=2026-04-01&duration_minutes=30"
```

### Book an Appointment

```bash
curl -X POST http://localhost:8000/calendar/appointment \
  -H "Content-Type: application/json" \
  -d '{
    "contact_name": "John Doe",
    "contact_email": "john@example.com",
    "start_time": "2026-04-01T14:00:00",
    "duration_minutes": 30,
    "title": "Sales Consultation"
  }'
```

## Testing

### Run Unit Tests

```bash
pytest tests/ -v
pytest tests/ --cov=src  # With coverage
```

### Simulate a Call Flow

```bash
python scripts/simulate_call.py
```

### Test Webhooks (requires running server)

```bash
# In one terminal:
uvicorn src.main:app --reload

# In another terminal:
python scripts/test_webhooks.py
```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

Key configurations:
- `RETELL_API_KEY` - Retell AI API key
- `VAPI_API_KEY` - Vapi AI API key
- `OPENAI_API_KEY` - OpenAI API key (for intent detection)
- `AIRTABLE_API_KEY` - Airtable API key
- `GHL_API_KEY` - GoHighLevel API key
- `CALENDAR_SERVICE` - Calendar provider (google, outlook, mock)

### Agent Persona

Customize the agent's behavior in `configs/agent_persona.yaml`:
- Agent name and description
- Voice configuration
- Greeting messages
- Fallback responses

### Routing Rules

Define conversation flows in `configs/routing_rules.yaml`:
- Intent-based routing
- State transitions
- Lead scoring
- Escalation rules

## Conversation Flow

### Default Flow

```
Greeting → Qualification → Booking → Farewell → End
```

### State Transitions

1. **Greeting** - Agent introduces itself and greets the caller
2. **Qualification** - Agent asks questions to understand needs
3. **Booking** - Agent schedules an appointment if appropriate
4. **Farewell** - Agent thanks caller and ends call
5. **Ended** - Call recording and data saved

### Intent Detection

The system detects intents:
- `schedule_appointment` - User wants to book a meeting
- `product_info` - User wants information about products
- `support_request` - User needs technical help
- `callback` - User wants a callback
- `general_inquiry` - General question
- `unknown` - Intent couldn't be determined

## Integrations

### Retell AI

Create web-based voice calls with automatic call recording and transcription.

```python
from src.voice.retell_client import RetellAIClient

client = RetellAIClient()
call = await client.create_web_call(
    agent_id="your_agent_id",
    user_phone_number="+1-555-0123"
)
```

### Vapi AI

Make outbound phone calls with AI voice agents.

```python
from src.voice.vapi_client import VapiAIClient

client = VapiAIClient()
call = await client.create_call(
    phone_number="+1-555-0123",
    assistant_id="your_assistant_id"
)
```

### Airtable

Automatically sync leads and calls to Airtable.

```python
from src.integrations.airtable_sync import AirtableSyncClient

airtable = AirtableSyncClient()
lead = await airtable.create_lead({
    "Name": "John Doe",
    "Email": "john@example.com",
    "Phone": "+1-555-0123",
    "Source": "Voice Call"
})
```

### GoHighLevel

Receive webhooks for contact and appointment events.

```python
from src.integrations.ghl_webhook import GoHighLevelWebhookHandler

handler = GoHighLevelWebhookHandler()
event = handler.parse_webhook_event("contact.created", data)
```

### Google Calendar

Check availability and book appointments.

```python
from src.integrations.calendar import CalendarFactory

calendar = CalendarFactory.create("google")
slots = await calendar.check_availability(date, duration_minutes=30)
appointment = await calendar.book_appointment(...)
```

## Development

### Code Style

```bash
# Format code
black src/

# Lint
flake8 src/

# Type checking
mypy src/
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

### Building Docker Image

```bash
docker build -t ai-voice-agent:latest .
```

## Performance Considerations

- Webhook timeouts: 30 seconds (configurable)
- Max retry attempts: 3 (configurable)
- Redis caching for conversation state (optional)
- Async/await for non-blocking I/O
- Connection pooling for HTTP clients

## Security

- Environment variable management with `.env`
- Webhook signature verification
- CORS middleware configuration
- Non-root Docker user
- No credentials in logs

## Monitoring & Logging

The application uses structured logging with `structlog` and JSON output format.

```python
logger = get_logger(__name__)
logger.info("Event occurred", key="value", conversation_id="123")
```

Logs include:
- Request/response logging
- Webhook event tracking
- API call metrics
- Error and exception details

## Troubleshooting

### Webhook not receiving events
- Verify webhook URL is publicly accessible
- Check signature verification in logs
- Ensure correct event types are configured

### Intent detection not working
- Verify `OPENAI_API_KEY` is set
- Check that OpenAI has API credits
- Review detected intent vs. expected in logs

### Airtable sync failing
- Verify `AIRTABLE_API_KEY` and `AIRTABLE_BASE_ID`
- Check table names match configuration
- Review Airtable field schemas

### Calendar integration errors
- Verify calendar service credentials
- Check calendar availability settings
- Review calendar integration logs

## Roadmap

- [ ] Multi-language support
- [ ] Advanced NLU with custom intents
- [ ] Real-time call transcription
- [ ] Sentiment analysis during calls
- [ ] Advanced lead scoring
- [ ] A/B testing framework
- [ ] Analytics dashboard
- [ ] SMS notification support
- [ ] Voice customization per campaign
- [ ] Integration with Zapier/Make.com

## Contributing

This is a proof-of-concept. To extend functionality:

1. Add new voice providers in `src/voice/`
2. Add new CRM integrations in `src/integrations/`
3. Extend intent detection in `src/agent/intent_router.py`
4. Add tests in `tests/`

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Review documentation in this README
- Check logs for detailed error messages
- Review API response payloads
- Test with `scripts/test_webhooks.py`

## Credits

Built with:
- FastAPI
- Retell AI
- Vapi AI
- OpenAI
- Airtable API
- Google Calendar API

---

**Version:** 0.1.0
**Last Updated:** 2026-03-28
