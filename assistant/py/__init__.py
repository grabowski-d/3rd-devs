"""Assistant module for AI planning and reasoning.

Implements a multi-phase reasoning system with:
- Thinking phase: Environment, personality, memory, tools analysis
- Planning phase: Task decomposition and action planning
- Action phase: Tool execution and result handling
"""

from .types import (
    Config,
    Task,
    Action,
    Document,
    Memory,
    Tool,
    State,
    ActionResult,
)
from .assistant_service import AssistantService

__version__ = "1.0.0"
__all__ = [
    "AssistantService",
    "Config",
    "Task",
    "Action",
    "Document",
    "Memory",
    "Tool",
    "State",
    "ActionResult",
]
