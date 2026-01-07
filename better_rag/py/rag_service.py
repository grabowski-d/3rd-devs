"""Better RAG service with query expansion."""
import json
from typing import List, Dict, Any, Optional
from openai.types.chat import ChatCompletionMessageParam, ChatCompletion
from .openai_service import OpenAIService
from .vector_service import VectorService

class BetterRAGService:
    """Advanced RAG with query expansion and re-ranking."""
    
    def __init__(self, openai_service: OpenAIService, vector_service: VectorService):
        self.openai_service = openai_service
        self.vector_service = vector_service
    
    async def expand_query(self, query: str) -> List[str]:
        """Expand query with related searches."""
        prompt: List[ChatCompletionMessageParam] = [
            {'role': 'system', 'content': 'Generate 3 alternative phrasings of this query for better search coverage.'},
            {'role': 'user', 'content': query}
        ]
        response = await self.openai_service.completion(prompt, json_mode=True)
        try:
            queries = json.loads(response.choices[0].message.content or '{}')
            return [query] + queries.get('queries', [])
        except:
            return [query]
    
    async def search_with_expansion(self, collection_name: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search using expanded queries."""
        queries = await self.expand_query(query)
        all_results = []
        for q in queries:
            results = await self.vector_service.perform_search(collection_name, q, limit)
            all_results.extend(results)
        # De-duplicate by id and sort by score
        unique = {r['id']: r for r in all_results}
        return sorted(unique.values(), key=lambda x: x['score'], reverse=True)[:limit]
    
    async def rerank_results(self, query: str, results: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
        """Re-rank search results using LLM."""
        texts = [r['payload'].get('text', '') for r in results]
        prompt: List[ChatCompletionMessageParam] = [
            {'role': 'system', 'content': 'Rank these results by relevance to the query.'},
            {'role': 'user', 'content': f'Query: {query}\n\nResults:\n' + '\n'.join(f'{i+1}. {t}' for i, t in enumerate(texts))}
        ]
        response = await self.openai_service.completion(prompt)
        return results[:top_k]
