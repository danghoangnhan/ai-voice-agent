"""Text-to-Speech abstraction layer"""

from abc import ABC, abstractmethod
from typing import Optional
from enum import Enum
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TTSProvider(str, Enum):
    """Supported TTS providers"""
    GOOGLE = "google"
    AZURE = "azure"
    OPENAI = "openai"
    ELEVEN_LABS = "eleven_labs"


class TTSEngine(ABC):
    """Abstract base class for TTS engines"""

    @abstractmethod
    async def synthesize(self, text: str, voice_id: Optional[str] = None) -> bytes:
        """Synthesize text to speech"""
        pass


class OpenAITTSEngine(TTSEngine):
    """OpenAI Text-to-Speech engine"""

    def __init__(self, api_key: str, model: str = "tts-1-hd", voice: str = "alloy"):
        """Initialize OpenAI TTS engine"""
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.voice = voice

    async def synthesize(self, text: str, voice_id: Optional[str] = None) -> bytes:
        """Synthesize text using OpenAI"""
        try:
            response = await self.client.audio.speech.create(
                model=self.model,
                voice=voice_id or self.voice,
                input=text,
            )
            logger.info("Synthesized speech with OpenAI", text_length=len(text))
            return response.content
        except Exception as e:
            logger.error("Failed to synthesize speech", error=str(e))
            raise


class ElevenLabsTTSEngine(TTSEngine):
    """ElevenLabs Text-to-Speech engine"""

    def __init__(self, api_key: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        """Initialize ElevenLabs TTS engine"""
        import httpx

        self.api_key = api_key
        self.voice_id = voice_id
        self.client = httpx.AsyncClient()

    async def synthesize(self, text: str, voice_id: Optional[str] = None) -> bytes:
        """Synthesize text using ElevenLabs"""
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id or self.voice_id}"
            headers = {"xi-api-key": self.api_key}
            payload = {"text": text, "model_id": "eleven_monolingual_v1"}

            response = await self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info("Synthesized speech with ElevenLabs", text_length=len(text))
            return response.content
        except Exception as e:
            logger.error("Failed to synthesize speech", error=str(e))
            raise


class MockTTSEngine(TTSEngine):
    """Mock TTS engine for testing"""

    async def synthesize(self, text: str, voice_id: Optional[str] = None) -> bytes:
        """Return mock audio bytes"""
        logger.info("Mock TTS synthesize called", text_length=len(text))
        return b"mock_audio_data"


class TTSFactory:
    """Factory for creating TTS engines"""

    @staticmethod
    def create(provider: TTSProvider, **kwargs) -> TTSEngine:
        """Create a TTS engine instance"""
        if provider == TTSProvider.OPENAI:
            return OpenAITTSEngine(**kwargs)
        elif provider == TTSProvider.ELEVEN_LABS:
            return ElevenLabsTTSEngine(**kwargs)
        else:
            return MockTTSEngine()
