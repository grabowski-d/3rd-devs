"""Context management service."""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ContextItem:
    """Single context item."""
    key: str
    value: Any
    importance: float = 1.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: Optional[str] = None


class ContextService:
    """Service for managing application context."""

    def __init__(self, max_items: int = 100):
        """Initialize context service.
        
        Args:
            max_items: Maximum items to store
        """
        self.context: Dict[str, ContextItem] = {}
        self.max_items = max_items
        logger.info(f"Initialized context service (max {max_items} items)")

    def set(
        self,
        key: str,
        value: Any,
        importance: float = 1.0,
        expires_at: Optional[str] = None,
    ) -> None:
        """Set context value.
        
        Args:
            key: Context key
            value: Context value
            importance: Importance score 0-1
            expires_at: ISO datetime when context expires
        """
        if len(self.context) >= self.max_items:
            # Remove least important item
            min_key = min(
                self.context.keys(),
                key=lambda k: self.context[k].importance,
            )
            del self.context[min_key]
        
        self.context[key] = ContextItem(
            key=key,
            value=value,
            importance=importance,
            expires_at=expires_at,
        )
        logger.debug(f"Set context: {key}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get context value.
        
        Args:
            key: Context key
            default: Default value if not found
            
        Returns:
            Context value or default
        """
        item = self.context.get(key)
        if item:
            # Check expiration
            if item.expires_at:
                expires = datetime.fromisoformat(item.expires_at)
                if datetime.now() > expires:
                    del self.context[key]
                    return default
            return item.value
        return default

    def get_all(self) -> Dict[str, Any]:
        """Get all context values.
        
        Returns:
            Dictionary of all context
        """
        return {k: v.value for k, v in self.context.items()}

    def clear(self) -> None:
        """Clear all context."""
        self.context.clear()
        logger.info("Cleared context")

    def delete(self, key: str) -> None:
        """Delete context key.
        
        Args:
            key: Key to delete
        """
        if key in self.context:
            del self.context[key]
            logger.debug(f"Deleted context: {key}")
