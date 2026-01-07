"""Vector Service with Qdrant - Python implementation of embedding/VectorService.ts"""
import uuid
import json
import os
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai_service import OpenAIService

class VectorService:
    def __init__(self, openai_service: OpenAIService):
        self.client = QdrantClient(
            url=os.getenv('QDRANT_URL'),
            api_key=os.getenv('QDRANT_API_KEY')
        )
        self.openai_service = openai_service
    
    async def ensure_collection(self, name: str) -> None:
        collections = self.client.get_collections()
        if not any(c.name == name for c in collections.collections):
            self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
            )
    
    async def initialize_collection_with_data(
        self,
        name: str,
        points: List[Dict[str, Any]]
    ) -> None:
        collections = self.client.get_collections()
        if not any(c.name == name for c in collections.collections):
            await self.ensure_collection(name)
            await self.add_points(name, points)
    
    async def add_points(
        self,
        collection_name: str,
        points: List[Dict[str, Any]]
    ) -> None:
        points_to_upsert = []
        
        for point in points:
            embedding = await self.openai_service.create_embedding(point.get('text', ''))
            points_to_upsert.append({
                'id': point.get('id', str(uuid.uuid4())),
                'vector': embedding,
                'payload': {
                    'text': point.get('text'),
                    **(point.get('metadata', {}))
                }
            })
        
        points_file_path = os.path.join(os.path.dirname(__file__), 'points.json')
        with open(points_file_path, 'w') as f:
            json.dump(points_to_upsert, f, indent=2)
        
        qdrant_points = [
            PointStruct(
                id=p['id'],
                vector=p['vector'],
                payload=p['payload']
            )
            for p in points_to_upsert
        ]
        
        self.client.upsert(
            collection_name=collection_name,
            wait=True,
            points=qdrant_points
        )
    
    async def perform_search(
        self,
        collection_name: str,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        query_embedding = await self.openai_service.create_embedding(query)
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=limit,
            with_payload=True
        )
        return results
