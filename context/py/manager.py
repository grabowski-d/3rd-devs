"""Context manager."""
from typing import Dict, Any
class ContextManager:
    def __init__(self):
        self.context: Dict[str, Any] = {}
    def set(self, key: str, value: Any) -> None:
        self.context[key] = value
    def get(self, key: str, default: Any = None) -> Any:
        return self.context.get(key, default)
    def clear(self) -> None:
        self.context.clear()
