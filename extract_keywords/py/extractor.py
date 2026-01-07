"""Keyword extraction."""
from typing import List
class KeywordExtractor:
    @staticmethod
    def extract(text: str, top_n: int = 10) -> List[str]:
        words = text.lower().split()
        freq = {}
        for word in words:
            if len(word) > 3:
                freq[word] = freq.get(word, 0) + 1
        return sorted(freq, key=freq.get, reverse=True)[:top_n]
