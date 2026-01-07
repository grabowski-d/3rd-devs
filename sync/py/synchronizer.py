"""Data sync utilities."""
import asyncio
from typing import List, Any
class Synchronizer:
    async def sync_batch(self, tasks: List) -> List[Any]:
        return await asyncio.gather(*tasks)
