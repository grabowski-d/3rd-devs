"""LLM chain orchestration module.

Implements chains of LLM calls with:
- Multi-step reasoning
- Context preservation
- Error handling
"""

from .chain_service import ChainService
from .openai_service import OpenAIService

__version__ = "1.0.0"
__all__ = ["ChainService", "OpenAIService"]
