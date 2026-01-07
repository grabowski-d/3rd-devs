"""Embedding service for text vectorization."""

import logging
from typing import List, Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for creating text embeddings."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize embedding service.
        
        Args:
            api_key: OpenAI API key
        """
        if not OpenAI:
            raise ImportError("openai package required")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "text-embedding-3-large"
        logger.info(f"Initialized embedding service ({self.model})")

    async def embed(self, text: str) -> List[float]:
        """Create embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
            )
            embedding = response.data[0].embedding
            logger.debug(f"Created embedding (dim={len(embedding)})")
            return embedding
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts,
            )
            embeddings = [item.embedding for item in response.data]
            logger.debug(f"Created {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"Batch embedding error: {e}")
            raise
