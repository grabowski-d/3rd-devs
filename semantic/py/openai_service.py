"""OpenAI semantic service."""

import os
from typing import List, Optional
from openai import AsyncOpenAI, OpenAI


class OpenAIService:
    """OpenAI service for semantic operations."""

    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.async_client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding."""
        response = await self.async_client.embeddings.create(
            model="text-embedding-3-large", input=text
        )
        return response.data[0].embedding
