"""Task completion and routing module.

Provides:
- Intent detection and categorization
- Task routing
- Completion scoring
"""

from .completion_service import CompletionService

__version__ = "1.0.0"
__all__ = ["CompletionService"]
