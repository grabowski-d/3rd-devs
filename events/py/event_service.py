"""Event service implementation."""

from typing import Callable, List


class EventService:
    """Service for event management."""

    def __init__(self):
        self.listeners: dict = {}

    def subscribe(self, event_name: str, callback: Callable):
        """Subscribe to event."""
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)

    def emit(self, event_name: str, data: dict):
        """Emit event."""
        if event_name in self.listeners:
            for callback in self.listeners[event_name]:
                callback(data)
