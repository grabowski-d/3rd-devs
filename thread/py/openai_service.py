"""OpenAI service for thread module."""
import os
from typing import Union, List, Optional, AsyncIterator, Dict, Any
from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessageParam


class OpenAIService:
    """OpenAI API wrapper for thread conversations."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI service.
        
        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)

    async def completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = 'gpt-4',
        stream: bool = False
    ) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        """Generate a chat completion.
        
        Args:
            messages: List of chat messages.
            model: Model name (default: gpt-4).
            stream: Whether to stream response (default: False).
        
        Returns:
            ChatCompletion or async iterator of chunks if streaming.
        """
        try:
            completion = self.client.chat.completions.create(
                messages=messages,
                model=model,
                stream=stream,
            )

            if stream:
                return completion
            else:
                return completion

        except Exception as error:
            raise ValueError(f'Error in OpenAI completion: {error}')
