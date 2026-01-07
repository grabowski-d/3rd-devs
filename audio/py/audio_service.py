"""High-level audio service with multiple providers."""

import logging
import io
from typing import Optional, Union

logger = logging.getLogger(__name__)


class AudioService:
    """Service for audio operations across multiple providers."""

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        elevenlabs_api_key: Optional[str] = None,
        groq_api_key: Optional[str] = None,
    ) -> None:
        """Initialize audio service.

        Args:
            openai_api_key: OpenAI API key
            elevenlabs_api_key: ElevenLabs API key
            groq_api_key: Groq API key
        """
        from .openai_service import OpenAIService
        
        self.openai = OpenAIService(openai_api_key)
        self.elevenlabs_key = elevenlabs_api_key
        self.groq_key = groq_api_key
        logger.info("Initialized audio service")

    async def text_to_speech_openai(
        self,
        text: str,
        voice: str = "alloy",
    ) -> bytes:
        """Convert text to speech using OpenAI.

        Args:
            text: Text to convert
            voice: Voice name

        Returns:
            Audio bytes
        """
        return await self.openai.speak(text, voice)

    async def text_to_speech_elevenlabs(
        self,
        text: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",
        model_id: str = "eleven_turbo_v2_5",
    ) -> Optional[bytes]:
        """Convert text to speech using ElevenLabs.

        Args:
            text: Text to convert
            voice_id: ElevenLabs voice ID
            model_id: ElevenLabs model ID

        Returns:
            Audio bytes or None if API key not configured
        """
        if not self.elevenlabs_key:
            logger.warning("ElevenLabs API key not configured")
            return None
        
        try:
            from elevenlabs.client import ElevenLabs
            
            client = ElevenLabs(api_key=self.elevenlabs_key)
            audio = client.generate(
                text=text,
                voice=voice_id,
                model=model_id,
            )
            
            audio_bytes = b""
            for chunk in audio:
                audio_bytes += chunk
            
            logger.debug(f"ElevenLabs speech generated ({len(audio_bytes)} bytes)")
            return audio_bytes
        except Exception as e:
            logger.error(f"Error with ElevenLabs: {e}")
            return None

    async def speech_to_text_openai(
        self,
        audio_data: Union[bytes, io.BytesIO],
        language: str = "pl",
    ) -> str:
        """Convert speech to text using OpenAI Whisper.

        Args:
            audio_data: Audio bytes or file-like object
            language: Language code

        Returns:
            Transcribed text
        """
        return await self.openai.transcribe(audio_data, language)

    async def speech_to_text_groq(
        self,
        audio_data: Union[bytes, io.BytesIO],
        language: str = "pl",
    ) -> Optional[str]:
        """Convert speech to text using Groq Whisper.

        Args:
            audio_data: Audio bytes or file-like object
            language: Language code

        Returns:
            Transcribed text or None if API key not configured
        """
        if not self.groq_key:
            logger.warning("Groq API key not configured")
            return None
        
        try:
            from groq import Groq
            
            client = Groq(api_key=self.groq_key)
            
            if isinstance(audio_data, bytes):
                audio_file = io.BytesIO(audio_data)
                audio_file.name = "audio.mp3"
            else:
                audio_file = audio_data
            
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                language=language,
            )
            
            logger.debug("Audio transcribed with Groq")
            return transcription.text
        except Exception as e:
            logger.error(f"Error with Groq: {e}")
            return None
