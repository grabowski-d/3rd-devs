"""Langfuse service for LLM observability."""

import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class TraceEvent:
    """Trace event for monitoring."""
    event_id: str
    event_type: str
    name: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    duration_ms: int
    model: str
    timestamp: str
    metadata: Dict[str, Any] = None


class LangfuseService:
    """Service for Langfuse integration."""

    def __init__(self, public_key: Optional[str] = None, secret_key: Optional[str] = None):
        """Initialize Langfuse service.
        
        Args:
            public_key: Langfuse public key
            secret_key: Langfuse secret key
        """
        self.public_key = public_key
        self.secret_key = secret_key
        self.events: Dict[str, TraceEvent] = {}
        
        try:
            from langfuse import Langfuse
            if public_key and secret_key:
                self.langfuse = Langfuse(
                    public_key=public_key,
                    secret_key=secret_key,
                )
            else:
                self.langfuse = None
                logger.warning("Langfuse credentials not configured")
        except ImportError:
            self.langfuse = None
            logger.warning("langfuse package not installed")

    def log_llm_call(
        self,
        event_id: str,
        name: str,
        input_tokens: int,
        output_tokens: int,
        model: str,
        duration_ms: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TraceEvent:
        """Log LLM call.
        
        Args:
            event_id: Unique event ID
            name: Name of the LLM call
            input_tokens: Input token count
            output_tokens: Output token count
            model: Model name
            duration_ms: Duration in milliseconds
            metadata: Additional metadata
            
        Returns:
            TraceEvent
        """
        total_tokens = input_tokens + output_tokens
        
        event = TraceEvent(
            event_id=event_id,
            event_type="llm_call",
            name=name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            duration_ms=duration_ms,
            model=model,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {},
        )
        
        self.events[event_id] = event
        
        if self.langfuse:
            try:
                self.langfuse.log_llm_call(
                    name=name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    model=model,
                )
            except Exception as e:
                logger.error(f"Error logging to Langfuse: {e}")
        
        logger.debug(f"Logged LLM call: {name} ({total_tokens} tokens)")
        return event

    def get_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics.
        
        Returns:
            Statistics dict
        """
        if not self.events:
            return {}
        
        total_input = sum(e.input_tokens for e in self.events.values())
        total_output = sum(e.output_tokens for e in self.events.values())
        total_duration = sum(e.duration_ms for e in self.events.values())
        
        return {
            "total_events": len(self.events),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "total_duration_ms": total_duration,
            "avg_duration_ms": total_duration / len(self.events) if self.events else 0,
        }
