"""Completion service for task routing."""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)


@dataclass
class RouteResult:
    """Result of routing operation."""
    category: str
    confidence: float
    intent: str


class CompletionService:
    """Service for task completion and routing."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize completion service.
        
        Args:
            api_key: OpenAI API key
        """
        if not OpenAI:
            raise ImportError("openai package required")
        
        self.client = OpenAI(api_key=api_key)
        self.categories = [
            "support", "sales", "technical", "billing", "general"
        ]
        logger.info("Initialized completion service")

    async def route(
        self,
        message: str,
        categories: Optional[List[str]] = None,
    ) -> RouteResult:
        """Route message to appropriate category.
        
        Args:
            message: Message to route
            categories: Available categories
            
        Returns:
            RouteResult with category and confidence
        """
        if categories is None:
            categories = self.categories
        
        categories_str = ", ".join(categories)
        
        prompt = f"""Categorize this message into one of: {categories_str}
Respond with JSON: {{"category": "...", "confidence": 0.0-1.0, "intent": "..."}}

Message: {message}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a task routing assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
            )
            
            content = response.choices[0].message.content or "{}"
            result = json.loads(content)
            
            return RouteResult(
                category=result.get("category", categories[0]),
                confidence=result.get("confidence", 0.5),
                intent=result.get("intent", message),
            )
        except Exception as e:
            logger.error(f"Routing error: {e}")
            return RouteResult(category=categories[0], confidence=0.5, intent=message)
