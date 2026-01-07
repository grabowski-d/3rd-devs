"""File operations service."""

import os
from typing import Optional


class FileService:
    """Service for file operations."""

    @staticmethod
    async def read_file(path: str) -> str:
        """Read file contents."""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    async def write_file(path: str, content: str):
        """Write file contents."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    async def list_files(directory: str) -> list:
        """List files in directory."""
        return os.listdir(directory)
