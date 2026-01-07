"""File service example."""

import asyncio
from .file_service import FileService


async def main():
    print("\n" + "="*60)
    print("File Service Example")
    print("="*60 + "\n")

    file_service = FileService()
    print("File service initialized.")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
