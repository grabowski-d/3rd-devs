"""LLM chain service for multi-step reasoning."""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from .openai_service import OpenAIService

logger = logging.getLogger(__name__)


@dataclass
class ChainConfig:
    """Chain configuration."""
    name: str
    description: str
    steps: int = 1
    temperature: float = 0.7
    max_tokens: int = 500


class ChainService:
    """Service for orchestrating LLM chains."""

    def __init__(self, openai_service: Optional[OpenAIService] = None):
        """Initialize chain service.
        
        Args:
            openai_service: OpenAI service instance
        """
        self.openai = openai_service or OpenAIService()
        self.history: List[Dict[str, Any]] = []
        logger.info("Initialized chain service")

    async def select(
        self,
        question: str,
        options: List[str],
        system_prompt: str = "Select the most relevant option.",
    ) -> int:
        """Select best option from list using LLM.
        
        Args:
            question: Question to answer
            options: List of options
            system_prompt: System message
            
        Returns:
            Index of selected option
        """
        options_text = "\n".join(
            [f"{i+1}. {opt}" for i, opt in enumerate(options)]
        )
        
        messages = [
            {"role": "system", "content": f"{system_prompt}\n\nRespond with only the number (1-{len(options)})."},
            {"role": "user", "content": f"{question}\n\nOptions:\n{options_text}"},
        ]
        
        result = await self.openai.completion(
            messages,
            max_tokens=1,
            temperature=0,
        )
        
        try:
            return int(result.strip()) - 1
        except (ValueError, IndexError):
            logger.warning(f"Invalid selection: {result}")
            return 0

    async def answer(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Answer question with context.
        
        Args:
            question: Question to answer
            context: Context data
            system_prompt: Custom system prompt
            
        Returns:
            Answer text
        """
        if system_prompt is None:
            system_prompt = "You are a helpful assistant."
            if context:
                system_prompt += f"\n\nContext: {context}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ]
        
        # Add history if present
        if self.history:
            messages = messages[:1] + self.history + messages[1:]
        
        result = await self.openai.completion(messages)
        
        # Store in history
        self.history.append({"role": "user", "content": question})
        self.history.append({"role": "assistant", "content": result})
        
        # Keep history manageable
        if len(self.history) > 20:
            self.history = self.history[-20:]
        
        return result

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.history = []
        logger.debug("Cleared chain history")
