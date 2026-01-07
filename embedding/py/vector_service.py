"""Vector database service using Qdrant."""
import os
import json
from typing import List, Dict, Optional, Any
from uuid import uuid4
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from .openai_service import OpenAIService
from .text_service import IDoc


class VectorService:
    """Service for vector storage and search using Qdrant."""

    def __init__(self, openai_service: OpenAIService, qdrant_url: Optional[str] = None, qdrant_api_key: Optional[str] = None):
        """Initialize vector service.
        
        Args:
            openai_service: OpenAI service for embeddings.
            qdrant_url: Qdrant URL. If not provided, uses QDRANT_URL env var.
            qdrant_api_key: Qdrant API key. If not provided, uses QDRANT_API_KEY env var.
        """
        self.openai_service = openai_service
        qdrant_url = qdrant_url or os.getenv('QDRANT_URL', 'http://localhost:6333')
        qdrant_api_key = qdrant_api_key or os.getenv('QDRANT_API_KEY')
        
        self.client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key
        )

    async def ensure_collection(self, name: str, vector_size: int = 3072) -> None:
        """Ensure collection exists, create if not.
        
        Args:
            name: Collection name.
            vector_size: Vector dimension size.
        """
        try:
            self.client.get_collection(name)
        except Exception:
            # Collection doesn't exist, create it
            self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    async def initialize_collection_with_data(
        self,
        name: str,
        points: List[Dict[str, Any]]
    ) -> None:
        """Initialize collection with data points.
        
        Args:
            name: Collection name.
            points: List of points with 'text' and optional 'id', 'metadata'.
        """
        try:
            self.client.get_collection(name)
        except Exception:
            # Collection doesn't exist, create and populate
            await self.ensure_collection(name)
            await self.add_points(name, points)

    async def add_points(
        self,
        collection_name: str,
        points: List[Dict[str, Any]]
    ) -> None:
        """Add points to collection.
        
        Args:
            collection_name: Collection name.
            points: List of points with 'text' and optional 'id', 'metadata'.
        """
        points_to_upsert = []
        
        for point in points:
            text = point.get('text', '')
            if isinstance(point, IDoc):
                text = point.text
                metadata = point.metadata or {}
            else:
                metadata = point.get('metadata', {})
            
            # Create embedding
            embedding = await self.openai_service.create_embedding(text)
            
            point_id = point.get('id') if isinstance(point, dict) else str(uuid4())
            if not point_id:
                point_id = str(uuid4())
            
            payload = {
                'text': text,
                **metadata
            }
            
            points_to_upsert.append(
                PointStruct(
                    id=hash(point_id) % (2**31),  # Convert UUID to numeric id
                    vector=embedding,
                    payload=payload
                )
            )
        
        # Save points to file for reference
        points_file = 'points.json'
        with open(points_file, 'w') as f:
            json.dump(
                [{
                    'id': p.id,
                    'text': p.payload['text'],
                    'metadata': {k: v for k, v in p.payload.items() if k != 'text'}
                } for p in points_to_upsert],
                f,
                indent=2
            )
        
        # Upsert to Qdrant
        self.client.upsert(
            collection_name=collection_name,
            points=points_to_upsert,
            wait=True
        )

    async def perform_search(
        self,
        collection_name: str,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar documents.
        
        Args:
            collection_name: Collection name.
            query: Search query text.
            limit: Maximum results to return.
        
        Returns:
            List of search results with score and payload.
        """
        # Create embedding for query
        query_embedding = await self.openai_service.create_embedding(query)
        
        # Search in Qdrant
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=limit,
            with_payload=True
        )
        
        # Format results
        return [
            {
                'id': result.id,
                'score': result.score,
                'payload': result.payload
            }
            for result in results
        ]
