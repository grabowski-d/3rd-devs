"""Document loader."""
from typing import List
class DocumentLoader:
    @staticmethod
    async def load(path: str) -> List[str]:
        try:
            with open(path, 'r') as f:
                return f.readlines()
        except:
            return []
