"""Document loader example."""

import asyncio
from .document_loader import DocumentLoader


async def main():
    print("\n" + "="*60)
    print("Document Loader Example")
    print("="*60 + "\n")

    loader = DocumentLoader()
    print("Document loader initialized.")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
