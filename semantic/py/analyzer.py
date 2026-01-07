"""Semantic analyzer."""
from typing import Dict, List
class SemanticAnalyzer:
    def extract_keywords(self, text: str) -> List[str]:
        words = text.lower().split()
        return list(set([w for w in words if len(w) > 5]))
    def calculate_similarity(self, text1: str, text2: str) -> float:
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0
