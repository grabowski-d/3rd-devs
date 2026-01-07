"""Langfuse service implementation."""

import os
from typing import Any, Optional
from langfuse import Langfuse


class LangfuseService:
    """Langfuse tracing and observability."""

    def __init__(self):
        self.client = Langfuse(
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            host=os.getenv("LANGFUSE_HOST")
        )

    def trace(self, id: str, name: str, session_id: str):
        """Create trace."""
        return self.client.trace(id=id, name=name, session_id=session_id)

    def flush(self):
        """Flush events."""
        self.client.flush()
