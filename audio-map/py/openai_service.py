"""OpenAI service for audio processing including transcription and TTS."""

import os
from typing import Any, AsyncGenerator, Dict, List, Optional, Union
from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessageParam

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from elevenlabs import ElevenLabsClient
except ImportError:
    ElevenLabsClient = None


class OpenAIService:
    """Service for OpenAI operations including chat, speech, and embeddings."""

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        elevenlabs_api_key: Optional[str] = None,
        groq_api_key: Optional[str] = None,
    ):
        """Initialize OpenAI service.

        Args:
            openai_api_key: OpenAI API key. Defaults to OPENAI_API_KEY env var.
            elevenlabs_api_key: ElevenLabs API key. Defaults to ELEVENLABS_API_KEY env var.
            groq_api_key: Groq API key. Defaults to GROQ_API_KEY env var.
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.elevenlabs_api_key = elevenlabs_api_key or os.getenv(
            "ELEVENLABS_API_KEY"
        )
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")

        self.client = OpenAI(api_key=self.openai_api_key)
        self.async_client = AsyncOpenAI(api_key=self.openai_api_key)

        if ElevenLabsClient and self.elevenlabs_api_key:
            self.elevenlabs = ElevenLabsClient(api_key=self.elevenlabs_api_key)
        else:
            self.elevenlabs = None

        if Groq and self.groq_api_key:
            self.groq = Groq(api_key=self.groq_api_key)
        else:
            self.groq = None

    async def completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = "gpt-4o",
        stream: bool = False,
        temperature: float = 0,
        json_mode: bool = False,
        max_tokens: int = 4096,
    ) -> Union[ChatCompletion, AsyncGenerator[ChatCompletionChunk, None]]:
        """Get chat completion from OpenAI.

        Args:
            messages: List of chat messages.
            model: Model ID. Defaults to "gpt-4o".
            stream: Whether to stream. Defaults to False.
            temperature: Temperature for response. Defaults to 0.
            json_mode: Whether to use JSON mode. Defaults to False.
            max_tokens: Max tokens to generate. Defaults to 4096.

        Returns:
            ChatCompletion or async generator for streaming.
        """
        try:
            params = {
                "messages": messages,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream,
            }

            if json_mode:
                params["response_format"] = {"type": "json_object"}

            response = await self.async_client.chat.completions.create(**params)
            return response

        except Exception as error:
            print(f"Error in completion: {error}")
            raise

    def count_tokens(self, text: str) -> int:
        """Count tokens in text (approximate).

        Args:
            text: Text to count tokens for.

        Returns:
            Approximate token count.
        """
        # Rough approximation: 1 token ≈ 4 characters
        return len(text) // 4

    def parse_json_response(self, response: ChatCompletion) -> Dict[str, Any]:
        """Parse JSON response from model.

        Args:
            response: Chat completion response.

        Returns:
            Parsed JSON content.

        Raises:
            ValueError: If parsing fails.
        """
        try:
            import json

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response content")
            return json.loads(content)
        except Exception as error:
            print(f"Error parsing JSON: {error}")
            raise

    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector.
        """
        try:
            response = await self.async_client.embeddings.create(
                model="text-embedding-3-large",
                input=text,
            )
            return response.data[0].embedding
        except Exception as error:
            print(f"Error creating embedding: {error}")
            raise

    async def transcribe(
        self,
        audio_bytes: bytes,
        language: str = "pl",
    ) -> str:
        """Transcribe audio using Whisper.

        Args:
            audio_bytes: Audio file bytes.
            language: Language code. Defaults to "pl".

        Returns:
            Transcribed text.
        """
        try:
            import io

            # Convert bytes to file-like object
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.mp3"

            response = await self.async_client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
                language=language,
            )
            return response.text
        except Exception as error:
            print(f"Error in transcription: {error}")
            raise

    async def transcribe_groq(
        self,
        audio_bytes: bytes,
        language: str = "pl",
    ) -> str:
        """Transcribe audio using Groq Whisper.

        Args:
            audio_bytes: Audio file bytes.
            language: Language code. Defaults to "pl".

        Returns:
            Transcribed text.
        """
        if not self.groq:
            raise ValueError("Groq not configured")

        try:
            import io

            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.mp3"
            
            response = self.groq.audio.transcriptions.create(
                file=("audio.mp3", audio_file.getvalue()),
                model="whisper-large-v3",
                language=language,
            )
            return response.text
        except Exception as error:
            print(f"Error in Groq transcription: {error}")
            raise

    async def speak(
        self,
        text: str,
        voice: str = "alloy",
    ) -> bytes:
        """Convert text to speech using OpenAI.

        Args:
            text: Text to convert to speech.
            voice: Voice to use. Defaults to "alloy".

        Returns:
            Audio bytes.
        """
        try:
            response = await self.async_client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
            )
            return response.content
        except Exception as error:
            print(f"Error in speech synthesis: {error}")
            raise

    async def speak_eleven(
        self,
        text: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",
        model_id: str = "eleven_turbo_v2_5",
    ) -> AsyncGenerator[bytes, None]:
        """Convert text to speech using Eleven Labs.

        Args:
            text: Text to convert.
            voice_id: Voice ID to use.
            model_id: Model to use.

        Returns:
            Audio stream.
        """
        if not self.elevenlabs:
            raise ValueError("Eleven Labs not configured")

        try:
            response = self.elevenlabs.generate(
                voice=voice_id,
                text=text,
                model_id=model_id,
                stream=True,
            )
            for chunk in response:
                yield chunk
        except Exception as error:
            print(f"Error in Eleven Labs TTS: {error}")
            raise

    def is_stream_response(self, response: Any) -> bool:
        """Check if response is a stream.

        Args:
            response: Response to check.

        Returns:
            True if stream, False otherwise.
        """
        return hasattr(response, "__aiter__") or hasattr(response, "__iter__")
