"""External API example."""

import asyncio
from .external_service import ExternalService


async def main():
    print("\n" + "="*60)
    print("External API Service Example")
    print("="*60 + "\n")

    external = ExternalService()
    print("External service initialized.")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
