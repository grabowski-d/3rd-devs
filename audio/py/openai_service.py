"""OpenAI audio and speech services."""

import logging
import io
from typing import AsyncIterator, Dict, List, Optional, Union, Any

try:
    import openai
    from openai import OpenAI, AsyncOpenAI
    from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessageParam
except ImportError:
    openai = None

logger = logging.getLogger(__name__)


class OpenAIService:
    """OpenAI service for audio, chat, and embeddings."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize OpenAI service.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        if not openai:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )
        
        if api_key:
            openai.api_key = api_key
        
        self.client = OpenAI()
        self.async_client = AsyncOpenAI()
        logger.info("Initialized OpenAI service")

    async def count_tokens(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = "gpt-4o",
    ) -> int:
        """Count tokens in messages using tiktoken.

        Args:
            messages: List of chat messages
            model: Model name for tokenizer

        Returns:
            Number of tokens
        """
        try:
            import tiktoken
            
            encoding = tiktoken.encoding_for_model(model)
            
            token_count = 0
            for message in messages:
                token_count += 4  # Message overhead
                for key, value in message.items():
                    token_count += len(encoding.encode(str(value)))
            
            return token_count
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Rough estimate if tiktoken fails
            return sum(len(str(m).split()) * 1.3 for m in messages)

    async def completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = "gpt-4o",
        stream: bool = False,
        temperature: float = 0,
        json_mode: bool = False,
        max_tokens: int = 4096,
    ) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        """Get chat completion from OpenAI.

        Args:
            messages: Chat messages
            model: Model name
            stream: Whether to stream response
            temperature: Temperature for generation
            json_mode: Whether to use JSON mode
            max_tokens: Maximum tokens in response

        Returns:
            ChatCompletion or async iterator if streaming
        """
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=model,
                stream=stream,
                temperature=temperature,
                response_format={"type": "json_object"} if json_mode else {"type": "text"},
                max_tokens=max_tokens,
            )
            logger.debug(f"Completion request to {model}")
            return response
        except Exception as e:
            logger.error(f"Error in completion: {e}")
            raise

    def parse_json_response(self, response: ChatCompletion) -> Dict[str, Any]:
        """Parse JSON response from completion.

        Args:
            response: ChatCompletion response

        Returns:
            Parsed JSON dict or error dict
        """
        try:
            import json
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response content")
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error parsing JSON response: {e}")
            return {"error": "Failed to parse response", "result": False}

    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-large",
                input=text,
            )
            logger.debug("Embedding created")
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            raise

    async def speak(self, text: str, voice: str = "alloy") -> bytes:
        """Convert text to speech using OpenAI.

        Args:
            text: Text to convert
            voice: Voice name (alloy, echo, fable, onyx, nova, shimmer)

        Returns:
            Audio bytes (MP3)
        """
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
            )
            audio_bytes = b""
            for chunk in response.iter_bytes():
                audio_bytes += chunk
            logger.debug(f"Speech generated ({len(audio_bytes)} bytes)")
            return audio_bytes
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            raise

    async def transcribe(
        self,
        audio_data: Union[bytes, io.BytesIO],
        language: str = "pl",
        model: str = "whisper-1",
    ) -> str:
        """Transcribe audio using OpenAI Whisper.

        Args:
            audio_data: Audio bytes or file-like object
            language: Language code (e.g., 'pl' for Polish)
            model: Model to use

        Returns:
            Transcribed text
        """
        try:
            if isinstance(audio_data, bytes):
                audio_file = io.BytesIO(audio_data)
                audio_file.name = "audio.mp3"
            else:
                audio_file = audio_data
            
            transcription = self.client.audio.transcriptions.create(
                model=model,
                file=audio_file,
                language=language,
            )
            logger.debug("Audio transcribed")
            return transcription.text
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
