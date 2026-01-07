"""OpenAI service for chain-of-thought QA."""

import os
from typing import List, Optional
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletion


class OpenAIService:
    """Service for OpenAI chain-of-thought operations."""

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
        temperature: float = 0,
        max_tokens: int = 500,
    ) -> ChatCompletion:
        """Get completion from OpenAI.

        Args:
            messages: Chat messages.
            model: Model to use. Defaults to "gpt-4o".
            temperature: Temperature. Defaults to 0.
            max_tokens: Max tokens. Defaults to 500.

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
