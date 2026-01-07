"""Token counting implementation."""

from typing import List


class TokenCounter:
    """Count tokens in text."""

    @staticmethod
    def count(text: str) -> int:
        """Count tokens (approximate)."""
        # Rough approximation: 1 token ≈ 4 characters
        return len(text) // 4

    @staticmethod
    def truncate(text: str, max_tokens: int) -> str:
        """Truncate text to max tokens."""
        max_chars = max_tokens * 4
        return text[:max_chars]
