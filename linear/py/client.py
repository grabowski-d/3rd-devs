"""Linear client."""
import os
class LinearClient:
    def __init__(self):
        self.api_key = os.getenv('LINEAR_API_KEY')
    async def get_issues(self):
        return []
