"""Reranking functionality."""
from typing import List, Dict, Any
class Ranker:
    def rerank(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        return sorted(results, key=lambda x: x.get('score', 0), reverse=True)
