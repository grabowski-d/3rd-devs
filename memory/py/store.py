"""Memory store."""
from typing import Dict, Any, Optional
class MemoryStore:
    def __init__(self):
        self.store: Dict[str, Any] = {}
    def save(self, key: str, value: Any) -> None:
        self.store[key] = value
    def load(self, key: str) -> Optional[Any]:
        return self.store.get(key)
    def delete(self, key: str) -> None:
        self.store.pop(key, None)
