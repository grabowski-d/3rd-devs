"""Qdrant vector search example."""

import asyncio
from .vector_service import VectorService


async def main():
    print("\n" + "="*60)
    print("Qdrant Vector Search Example")
    print("="*60 + "\n")

    vector_service = VectorService()
    print("Qdrant service initialized.\n")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
