"""OpenAI service for context retrieval."""

import os
from typing import List, Optional
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletion


class OpenAIService:
    """Service for OpenAI context operations."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI service.

        Args:
            api_key: OpenAI API key. Defaults to OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

    async def completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> ChatCompletion:
        """Get completion with document context.

        Args:
            messages: Chat messages.
            model: Model to use. Defaults to "gpt-4o".
            temperature: Temperature. Defaults to 0.7.
            max_tokens: Max tokens. Defaults to 2048.

        Returns:
            Chat completion.
        """
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response
        except Exception as error:
            print(f"Error in completion: {error}")
            raise
