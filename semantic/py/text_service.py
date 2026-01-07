"""Text processing for semantic search."""

from typing import List


class TextService:
    """Service for text processing and preprocessing."""

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text."""
        return text.lower().strip()

    @staticmethod
    def split_text(text: str, chunk_size: int = 512) -> List[str]:
        """Split text into chunks."""
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
