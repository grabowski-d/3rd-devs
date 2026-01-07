"""OpenAI service for chat completions."""

import os
from typing import AsyncGenerator, List, Optional, Union
from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessageParam


class OpenAIService:
    """Service for OpenAI chat completions."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI service.

        Args:
            api_key: OpenAI API key. Defaults to OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)

    async def completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = "gpt-4o",
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Union[ChatCompletion, AsyncGenerator[ChatCompletionChunk, None]]:
        """Get chat completion.

        Args:
            messages: Chat messages.
            model: Model to use. Defaults to "gpt-4o".
            stream: Whether to stream. Defaults to False.
            temperature: Temperature. Defaults to 0.7.
            max_tokens: Max tokens. Defaults to 2048.

        Returns:
            ChatCompletion or async generator for streaming.
        """
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
            )
            return response
        except Exception as error:
            print(f"Error in completion: {error}")
            raise

    async def async_completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = "gpt-4o",
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Union[ChatCompletion, AsyncGenerator[ChatCompletionChunk, None]]:
        """Get async chat completion.

        Args:
            messages: Chat messages.
            model: Model to use. Defaults to "gpt-4o".
            stream: Whether to stream. Defaults to False.
            temperature: Temperature. Defaults to 0.7.
            max_tokens: Max tokens. Defaults to 2048.

        Returns:
            ChatCompletion or async generator for streaming.
        """
        try:
            response = await self.async_client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
            )
            return response
        except Exception as error:
            print(f"Error in async completion: {error}")
            raise
