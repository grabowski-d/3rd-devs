"""Hybrid search."""
from typing import List, Dict, Any
class HybridSearch:
    def combine_results(self, lexical: List[Dict], semantic: List[Dict]) -> List[Dict]:
        combined = {}
        for r in lexical:
            combined[r.get('id')] = r
        for r in semantic:
            if r.get('id') not in combined:
                combined[r.get('id')] = r
        return list(combined.values())
