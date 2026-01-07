"""Vector database service."""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import math

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Vector document."""
    id: str
    text: str
    embedding: List[float]
    metadata: Dict[str, Any] = None


class VectorService:
    """In-memory vector database service."""

    def __init__(self):
        """Initialize vector service."""
        self.documents: Dict[str, Document] = {}
        self.collections: Dict[str, List[str]] = {}
        logger.info("Initialized vector service")

    def add(self, doc_id: str, text: str, embedding: List[float], 
            metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add document to vector store.
        
        Args:
            doc_id: Document ID
            text: Document text
            embedding: Document embedding
            metadata: Document metadata
        """
        self.documents[doc_id] = Document(
            id=doc_id,
            text=text,
            embedding=embedding,
            metadata=metadata or {},
        )
        logger.debug(f"Added document: {doc_id}")

    def search(self, query_embedding: List[float], limit: int = 10) -> List[tuple]:
        """Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            limit: Maximum results
            
        Returns:
            List of (doc_id, similarity_score) tuples
        """
        results = []
        
        for doc_id, doc in self.documents.items():
            similarity = self._cosine_similarity(query_embedding, doc.embedding)
            results.append((doc_id, similarity))
        
        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)
        logger.debug(f"Search returned {len(results[:limit])} results")
        
        return results[:limit]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between vectors.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            Similarity score 0-1
        """
        dot_product = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x ** 2 for x in a))
        mag_b = math.sqrt(sum(x ** 2 for x in b))
        
        if mag_a == 0 or mag_b == 0:
            return 0
        
        return dot_product / (mag_a * mag_b)
