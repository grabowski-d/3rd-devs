"""Langfuse service."""
import os
try:
    from langfuse import Langfuse
except ImportError:
    Langfuse = None
class LangfuseService:
    def __init__(self):
        if Langfuse:
            self.client = Langfuse(
                secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
                public_key=os.getenv('LANGFUSE_PUBLIC_KEY')
            )
    async def flush(self) -> None:
        if self.client:
            self.client.flush()
