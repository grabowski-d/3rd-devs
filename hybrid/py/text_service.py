"""Text service for hybrid search."""

from typing import List, Dict


class TextService:
    """Text processing and hybrid search."""

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tokenize text."""
        return text.lower().split()

    @staticmethod
    def rank_results(lexical: List[Dict], semantic: List[Dict]) -> List[Dict]:
        """Combine and rank search results."""
        seen = set()
        results = []
        for item in lexical + semantic:
            id_ = item.get('id')
            if id_ not in seen:
                seen.add(id_)
                results.append(item)
        return results
