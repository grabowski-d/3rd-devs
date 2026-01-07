"""Text splitter."""
from typing import List
class TextSplitter:
    @staticmethod
    def split(text: str, chunk_size: int = 1000) -> List[str]:
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i+chunk_size])
        return chunks
