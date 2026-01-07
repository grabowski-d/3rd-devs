"""Type definitions for assistant module."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional
from datetime import datetime


@dataclass
class ActionResult:
    """Result of an action execution."""
    status: str
    data: Any


@dataclass
class MemoryCategory:
    """Category for organizing memories."""
    name: str
    description: str


@dataclass
class Tool:
    """Tool available for the assistant."""
    name: str
    description: str
    instruction: str = ""


@dataclass
class Config:
    """Assistant configuration."""
    max_steps: int
    step: int
    task: Optional[str]
    action: Optional[str]
    ai_name: str
    username: str
    environment: str
    personality: str
    memory_categories: List[MemoryCategory] = field(default_factory=list)
    tools: List[Tool] = field(default_factory=list)


@dataclass
class Action:
    """Action to be executed."""
    uuid: str
    task_uuid: str
    name: str
    tool_name: str
    payload: Dict[str, Any] = field(default_factory=dict)
    result: Optional[ActionResult] = None
    status: Literal["pending", "completed", "failed"] = "pending"
    sequence: int = 0
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Task:
    """Task to be completed."""
    uuid: str
    conversation_uuid: str
    name: str
    description: str
    status: Literal["pending", "completed", "failed"] = "pending"
    actions: List[Action] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Document:
    """Document stored in the assistant."""
    uuid: str
    conversation_uuid: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Memory:
    """Memory item for the assistant."""
    name: str
    category: str
    content: str


@dataclass
class Thoughts:
    """Thoughts from reasoning phases."""
    environment: str = ""
    personality: str = ""
    memory: str = ""
    tools: str = ""


@dataclass
class State:
    """Complete state of the assistant."""
    config: Config
    thoughts: Thoughts
    tasks: List[Task] = field(default_factory=list)
    documents: List[Document] = field(default_factory=list)
    memories: List[Memory] = field(default_factory=list)
    tools: List[Tool] = field(default_factory=list)
    messages: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for JSON serialization."""
        return {
            "config": {
                "max_steps": self.config.max_steps,
                "step": self.config.step,
                "task": self.config.task,
                "action": self.config.action,
                "ai_name": self.config.ai_name,
                "username": self.config.username,
                "environment": self.config.environment,
                "personality": self.config.personality,
            },
            "thoughts": {
                "environment": self.thoughts.environment,
                "personality": self.thoughts.personality,
                "memory": self.thoughts.memory,
                "tools": self.thoughts.tools,
            },
            "tasks": len(self.tasks),
            "documents": len(self.documents),
            "memories": len(self.memories),
            "messages": len(self.messages),
        }
