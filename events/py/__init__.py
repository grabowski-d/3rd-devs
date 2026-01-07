"""Event system module.

Provides:
- Event publishing and subscription
- Event handlers
- Event history
"""

from .event_service import EventService, Event

__version__ = "1.0.0"
__all__ = ["EventService", "Event"]
