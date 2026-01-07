"""Linear algebra operations."""

import numpy as np
from typing import List


class LinearService:
    """Service for linear algebra."""

    @staticmethod
    def dot_product(a: List[float], b: List[float]) -> float:
        """Calculate dot product."""
        return float(np.dot(a, b))

    @staticmethod
    def magnitude(vector: List[float]) -> float:
        """Calculate vector magnitude."""
        return float(np.linalg.norm(vector))

    @staticmethod
    def cosine_similarity(a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity."""
        dot = np.dot(a, b)
        mag_a = np.linalg.norm(a)
        mag_b = np.linalg.norm(b)
        return float(dot / (mag_a * mag_b)) if mag_a and mag_b else 0.0
