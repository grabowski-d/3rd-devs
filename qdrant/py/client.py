"""Qdrant client."""
import os
from qdrant_client import QdrantClient
class QdrantService:
    def __init__(self):
        self.client = QdrantClient(url=os.getenv('QDRANT_URL'))
