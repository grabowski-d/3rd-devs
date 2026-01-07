"""Tool registry."""
from typing import Dict, Callable
class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
    def register(self, name: str, tool: Callable) -> None:
        self.tools[name] = tool
    def get(self, name: str) -> Callable:
        return self.tools.get(name)
