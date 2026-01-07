"""OpenAI service for chain orchestration."""

import logging
from typing import Any, Dict, List, Optional

try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None

logger = logging.getLogger(__name__)


class OpenAIService:
    """OpenAI API wrapper for chaining."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize OpenAI service.
        
        Args:
            api_key: OpenAI API key
        """
        if not openai:
            raise ImportError("openai package required")
        
        if api_key:
            openai.api_key = api_key
        self.client = OpenAI()
        logger.info("Initialized OpenAI service")

    async def completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        max_tokens: int = 500,
        temperature: float = 0.7,
    ) -> str:
        """Get completion from OpenAI.
        
        Args:
            messages: Chat messages
            model: Model name
            max_tokens: Max response tokens
            temperature: Generation temperature
            
        Returns:
            Completion text
        """
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Completion error: {e}")
            raise
