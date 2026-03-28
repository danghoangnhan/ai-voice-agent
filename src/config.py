"""Configuration management for the AI Voice Agent"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # App Configuration
    app_env: str = os.getenv("APP_ENV", "development")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Retell AI Configuration
    retell_api_key: Optional[str] = os.getenv("RETELL_API_KEY")
    retell_agent_id: Optional[str] = os.getenv("RETELL_AGENT_ID")

    # Vapi AI Configuration
    vapi_api_key: Optional[str] = os.getenv("VAPI_API_KEY")
    vapi_phone_number: Optional[str] = os.getenv("VAPI_PHONE_NUMBER")

    # GoHighLevel Configuration
    ghl_api_key: Optional[str] = os.getenv("GHL_API_KEY")
    ghl_account_id: Optional[str] = os.getenv("GHL_ACCOUNT_ID")
    ghl_webhook_secret: Optional[str] = os.getenv("GHL_WEBHOOK_SECRET")

    # Airtable Configuration
    airtable_api_key: Optional[str] = os.getenv("AIRTABLE_API_KEY")
    airtable_base_id: Optional[str] = os.getenv("AIRTABLE_BASE_ID")
    airtable_leads_table: str = os.getenv("AIRTABLE_LEADS_TABLE", "Leads")
    airtable_calls_table: str = os.getenv("AIRTABLE_CALLS_TABLE", "Calls")

    # Calendar Configuration
    calendar_service: str = os.getenv("CALENDAR_SERVICE", "google")
    calendar_api_key: Optional[str] = os.getenv("CALENDAR_API_KEY")

    # OpenAI Configuration
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")

    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./voice_agent.db")

    # Webhook Configuration
    webhook_timeout: int = int(os.getenv("WEBHOOK_TIMEOUT", "30"))
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
