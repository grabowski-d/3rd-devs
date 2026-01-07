"""Embedding and semantic search module.

Provides:
- Text embeddings
- Semantic similarity
- Vector search
- Collection management
"""

from .embedding_service import EmbeddingService
from .vector_service import VectorService

__version__ = "1.0.0"
__all__ = ["EmbeddingService", "VectorService"]
