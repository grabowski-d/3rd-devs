"""Type definitions for agent system."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


@dataclass
class AllowedDomain:
    """Allowed domain for web search."""
    name: str
    url: str
    scrappable: bool


@dataclass
class IDoc:
    """Document with metadata."""
    uuid: str
    name: str
    description: str
    type: str
    content_type: str
    source: str
    conversation_uuid: str
    text: str


@dataclass
class SearchResult:
    """Search result from web search."""
    url: str
    title: str
    description: str
    content: Optional[str] = None


@dataclass
class Query:
    """Query for web search."""
    q: str
    url: str


@dataclass
class ActionResult:
    """Result of an action."""
    text: str
    metadata: Dict[str, Any]


@dataclass
class Action:
    """Action taken by agent."""
    uuid: str
    name: str
    parameters: str
    description: str
    results: List[ActionResult] = field(default_factory=list)
    tool_uuid: str = ""


@dataclass
class Config:
    """Agent configuration."""
    active_step: Optional[Dict[str, Any]] = None


@dataclass
class State:
    """Agent state."""
    messages: List[Dict[str, str]] = field(default_factory=list)
    documents: List[IDoc] = field(default_factory=list)
    actions: List[Action] = field(default_factory=list)
    config: Config = field(default_factory=Config)
    tools: List[Dict[str, str]] = field(default_factory=lambda: [
        {'name': 'web_search', 'description': 'Search the web for information', 'parameters': 'query: str'},
        {'name': 'final_answer', 'description': 'Provide final answer', 'parameters': 'answer: str'}
    ])
