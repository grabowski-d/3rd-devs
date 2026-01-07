"""External API integration."""

import httpx
from typing import Optional, Dict, Any


class ExternalService:
    """Service for external API calls."""

    async def get(self, url: str, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request."""
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            return response.json()

    async def post(self, url: str, data: Dict, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request."""
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)
            return response.json()
