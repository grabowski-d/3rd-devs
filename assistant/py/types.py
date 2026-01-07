"""Type definitions for assistant service."""

from typing import Any, Dict, List, Literal, Optional, TypedDict
from datetime import datetime


class MessageParam(TypedDict, total=False):
    """Chat completion message parameter."""

    role: Literal["system", "user", "assistant"]
    content: str


class MemoryCategory(TypedDict):
    """Memory category definition."""

    name: str
    description: str


class Tool(TypedDict):
    """Tool definition."""

    name: str
    description: str
    instruction: str


class Config(TypedDict):
    """Configuration for agent."""

    max_steps: int
    step: int
    task: Optional[str]
    action: Optional[str]
    ai_name: str
    username: str
    environment: str
    personality: str
    memory_categories: List[MemoryCategory]
    tools: List[Tool]


class ActionResult(TypedDict):
    """Result from action execution."""

    status: str
    data: Any


class Action(TypedDict):
    """Action to be executed."""

    uuid: str
    task_uuid: str
    name: str
    tool_name: str
    payload: Dict[str, Any]
    result: Optional[ActionResult]
    status: Literal["pending", "completed", "failed"]
    sequence: int
    description: str
    created_at: str
    updated_at: str


class Task(TypedDict):
    """Task to be planned and executed."""

    uuid: str
    conversation_uuid: str
    status: Literal["pending", "completed", "failed"]
    name: str
    description: str
    actions: List[Action]
    created_at: str
    updated_at: str


class Document(TypedDict):
    """Document in conversation context."""

    uuid: str
    conversation_uuid: str
    text: str
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str


class Memory(TypedDict):
    """Memory entry."""

    name: str
    category: str
    content: str


class Thoughts(TypedDict):
    """Agent thoughts from thinking phase."""

    environment: str
    personality: str
    memory: str
    tools: str


class State(TypedDict):
    """Complete state of the agent."""

    config: Config
    thoughts: Thoughts
    tasks: List[Task]
    documents: List[Document]
    memories: List[Memory]
    tools: List[Tool]
    messages: List[MessageParam]
