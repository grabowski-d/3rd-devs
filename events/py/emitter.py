"""Event emitter."""
from typing import Callable, Dict, List
class EventEmitter:
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}
    def on(self, event: str, handler: Callable) -> None:
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(handler)
    def emit(self, event: str, *args, **kwargs) -> None:
        if event in self.listeners:
            for handler in self.listeners[event]:
                handler(*args, **kwargs)
