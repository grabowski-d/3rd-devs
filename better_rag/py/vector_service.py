"""Vector service for better RAG."""
import os
import json
from typing import List, Dict, Optional, Any
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from .openai_service import OpenAIService

class VectorService:
    def __init__(self, openai_service: OpenAIService, qdrant_url: Optional[str] = None, qdrant_api_key: Optional[str] = None):
        self.openai_service = openai_service
        qdrant_url = qdrant_url or os.getenv('QDRANT_URL', 'http://localhost:6333')
        qdrant_api_key = qdrant_api_key or os.getenv('QDRANT_API_KEY')
        self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    
    async def ensure_collection(self, name: str, vector_size: int = 3072) -> None:
        try:
            self.client.get_collection(name)
        except Exception:
            self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
    
    async def add_points(self, collection_name: str, points: List[Dict[str, Any]]) -> None:
        points_to_upsert = []
        for point in points:
            text = point.get('text', '')
            embedding = await self.openai_service.create_embedding(text)
            points_to_upsert.append(
                PointStruct(id=hash(text) % (2**31), vector=embedding, payload=point)
            )
        with open('points.json', 'w') as f:
            json.dump([{'id': p.id, 'text': p.payload.get('text')} for p in points_to_upsert], f, indent=2)
        self.client.upsert(collection_name=collection_name, points=points_to_upsert, wait=True)
    
    async def perform_search(self, collection_name: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        query_embedding = await self.openai_service.create_embedding(query)
        results = self.client.search(collection_name=collection_name, query_vector=query_embedding, limit=limit, with_payload=True)
        return [{'id': r.id, 'score': r.score, 'payload': r.payload} for r in results]
