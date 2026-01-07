"""Langfuse service for tracing and observability."""

import os
from typing import Any, Dict, Optional, Union
from langfuse import Langfuse
from langfuse.client import StatefulClient


class LangfuseService:
    """Service for Langfuse integration."""

    def __init__(self):
        """Initialize Langfuse service."""
        self.langfuse = Langfuse(
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            host=os.getenv("LANGFUSE_HOST"),
        )

    def create_trace(self, id: str, name: str, session_id: str) -> StatefulClient:
        """Create a new trace.

        Args:
            id: Trace ID.
            name: Trace name.
            session_id: Session ID.

        Returns:
            Langfuse trace client.
        """
        return self.langfuse.trace(id=id, name=name, session_id=session_id)

    def create_span(
        self, trace: StatefulClient, name: str, input: Any = None
    ) -> StatefulClient:
        """Create a new span.

        Args:
            trace: Parent trace.
            name: Span name.
            input: Span input.

        Returns:
            Langfuse span client.
        """
        return trace.span(name=name, input=input)

    def finalize_span(
        self, span: StatefulClient, name: str, input: Any, output: Any
    ) -> None:
        """Finalize a span.

        Args:
            span: Span to finalize.
            name: New name (optional).
            input: Input data.
            output: Output data.
        """
        span.update(name=name, input=input, output=output)
        span.end()

    def finalize_trace(self, trace: StatefulClient, input: Any, output: Any) -> None:
        """Finalize a trace.

        Args:
            trace: Trace to finalize.
            input: Trace input.
            output: Trace output.
        """
        trace.update(input=input, output=output)

    def create_generation(
        self, trace: StatefulClient, name: str, input: Any, model: str = "gpt-4o"
    ) -> StatefulClient:
        """Create a generation.

        Args:
            trace: Parent trace.
            name: Generation name.
            input: Generation input.
            model: Model name.

        Returns:
            Langfuse generation client.
        """
        return trace.generation(name=name, input=input, model=model)

    def finalize_generation(
        self,
        generation: StatefulClient,
        output: Any,
        model: str,
        usage: Optional[Dict[str, int]] = None,
    ) -> None:
        """Finalize a generation.

        Args:
            generation: Generation to finalize.
            output: Generation output.
            model: Model name.
            usage: Token usage.
        """
        generation.update(output=output, model=model, usage=usage)
        generation.end()

    def create_event(
        self, trace: StatefulClient, name: str, input: Any = None, output: Any = None
    ) -> None:
        """Create an event.

        Args:
            trace: Parent trace.
            name: Event name.
            input: Event input.
            output: Event output.
        """
        trace.event(name=name, input=input, output=output)

    def flush(self) -> None:
        """Flush pending events."""
        self.langfuse.flush()

    def shutdown(self) -> None:
        """Shutdown Langfuse client."""
        self.langfuse.shutdown()
