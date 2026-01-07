"""Neo4j graph example."""

import asyncio
from .graph_service import GraphService


async def main():
    print("\n" + "="*60)
    print("Neo4j Graph Example")
    print("="*60 + "\n")

    graph = GraphService()
    print("Neo4j service initialized.")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
