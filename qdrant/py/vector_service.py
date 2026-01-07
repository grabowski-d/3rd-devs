"""Qdrant vector service."""

from typing import List


class VectorService:
    """Vector service using Qdrant."""

    def __init__(self, collection_name: str = "documents"):
        self.collection_name = collection_name

    async def add_vector(self, vector: List[float], metadata: dict):
        """Add vector to collection."""
        pass

    async def search(self, query_vector: List[float], k: int = 5):
        """Search vectors."""
        return []
