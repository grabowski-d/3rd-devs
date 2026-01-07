"""Event service for pub/sub pattern."""

import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Application event."""
    type: str
    data: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    source: str = "system"


class EventService:
    """Service for event-driven architecture."""

    def __init__(self, max_history: int = 1000):
        """Initialize event service.
        
        Args:
            max_history: Maximum events to keep in history
        """
        self.subscribers: Dict[str, List[Callable]] = {}
        self.history: List[Event] = []
        self.max_history = max_history
        logger.info("Initialized event service")

    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """Subscribe to event type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Async or sync function to handle event
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(handler)
        logger.debug(f"Subscribed to {event_type}")

    async def publish(self, event: Event) -> None:
        """Publish event.
        
        Args:
            event: Event to publish
        """
        # Store in history
        self.history.append(event)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        # Call handlers
        handlers = self.subscribers.get(event.type, [])
        for handler in handlers:
            try:
                # Support both async and sync handlers
                import asyncio
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
                logger.debug(f"Handler executed for {event.type}")
            except Exception as e:
                logger.error(f"Error in event handler: {e}")

    def get_history(self, event_type: Optional[str] = None) -> List[Event]:
        """Get event history.
        
        Args:
            event_type: Filter by event type (None for all)
            
        Returns:
            List of events
        """
        if event_type:
            return [e for e in self.history if e.type == event_type]
        return self.history

    def clear_history(self) -> None:
        """Clear event history."""
        self.history.clear()
        logger.info("Cleared event history")
