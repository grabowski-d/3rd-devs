"""OpenAI service for handling chat completions and AI interactions."""

from typing import Any, AsyncGenerator, Dict, List, Optional, Union
from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessageParam
import os


class OpenAIService:
    """Service for interacting with OpenAI API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI service.

        Args:
            api_key: OpenAI API key. Defaults to OPENAI_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)

    async def completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = "gpt-4o",
        stream: bool = False,
        json_mode: bool = False,
        max_tokens: int = 8096,
    ) -> Union[ChatCompletion, AsyncGenerator[ChatCompletionChunk, None]]:
        """Get completion from OpenAI.

        Args:
            messages: List of chat messages.
            model: Model ID to use. Defaults to "gpt-4o".
            stream: Whether to stream the response. Defaults to False.
            json_mode: Whether to use JSON mode for structured output. Defaults to False.
            max_tokens: Maximum tokens to generate. Defaults to 8096.

        Returns:
            ChatCompletion or async generator of ChatCompletionChunk depending on stream.

        Raises:
            ValueError: If API key is not configured.
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")

        try:
            # Some models don't support certain parameters
            supports_features = model not in ("o1-mini", "o1-preview")

            response_format = None
            if json_mode and supports_features:
                response_format = {"type": "json_object"}
            elif supports_features:
                response_format = {"type": "text"}

            params = {
                "messages": messages,
                "model": model,
            }

            if supports_features:
                params["stream"] = stream
                params["max_tokens"] = max_tokens
                if response_format:
                    params["response_format"] = response_format

            response = self.client.chat.completions.create(**params)

            return response

        except Exception as error:
            print(f"Error in OpenAI completion: {error}")
            raise

    async def async_completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = "gpt-4o",
        stream: bool = False,
        json_mode: bool = False,
        max_tokens: int = 8096,
    ) -> Union[ChatCompletion, AsyncGenerator[ChatCompletionChunk, None]]:
        """Get async completion from OpenAI.

        Args:
            messages: List of chat messages.
            model: Model ID to use. Defaults to "gpt-4o".
            stream: Whether to stream the response. Defaults to False.
            json_mode: Whether to use JSON mode for structured output. Defaults to False.
            max_tokens: Maximum tokens to generate. Defaults to 8096.

        Returns:
            ChatCompletion or async generator of ChatCompletionChunk depending on stream.
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")

        try:
            supports_features = model not in ("o1-mini", "o1-preview")

            response_format = None
            if json_mode and supports_features:
                response_format = {"type": "json_object"}
            elif supports_features:
                response_format = {"type": "text"}

            params = {
                "messages": messages,
                "model": model,
            }

            if supports_features:
                params["stream"] = stream
                params["max_tokens"] = max_tokens
                if response_format:
                    params["response_format"] = response_format

            response = await self.async_client.chat.completions.create(**params)

            return response

        except Exception as error:
            print(f"Error in async OpenAI completion: {error}")
            raise
