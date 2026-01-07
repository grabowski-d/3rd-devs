"""Keyword extraction implementation."""

from typing import List


class KeywordExtractor:
    """Extract keywords from text."""

    async def extract(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords."""
        words = text.lower().split()
        return list(set(words))[:max_keywords]
