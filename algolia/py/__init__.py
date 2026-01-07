"""Algolia search integration module.

Provides high-level interface for Algolia search operations including:
- Single and multi-index search
- Object CRUD operations
- Batch operations
- Index management
"""

from .algolia_service import AlgoliaService
from .app import main

__version__ = "1.0.0"
__all__ = ["AlgoliaService", "main"]
