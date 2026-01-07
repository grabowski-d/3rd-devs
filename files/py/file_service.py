"""File management service."""

import logging
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    """File metadata."""
    path: str
    name: str
    size: int
    created_at: str
    modified_at: str
    hash: str
    is_directory: bool = False


class FileService:
    """Service for file management."""

    def __init__(self, base_path: str = "."):
        """Initialize file service.
        
        Args:
            base_path: Base directory for file operations
        """
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
        logger.info(f"Initialized file service ({base_path})")

    def create(self, path: str, content: str) -> FileInfo:
        """Create file.
        
        Args:
            path: File path
            content: File content
            
        Returns:
            FileInfo
        """
        full_path = os.path.join(self.base_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w") as f:
            f.write(content)
        
        return self.get_info(path)

    def read(self, path: str) -> str:
        """Read file.
        
        Args:
            path: File path
            
        Returns:
            File content
        """
        full_path = os.path.join(self.base_path, path)
        with open(full_path, "r") as f:
            return f.read()

    def update(self, path: str, content: str) -> FileInfo:
        """Update file.
        
        Args:
            path: File path
            content: New content
            
        Returns:
            FileInfo
        """
        return self.create(path, content)

    def delete(self, path: str) -> None:
        """Delete file.
        
        Args:
            path: File path
        """
        full_path = os.path.join(self.base_path, path)
        if os.path.isfile(full_path):
            os.remove(full_path)
            logger.debug(f"Deleted file: {path}")

    def get_info(self, path: str) -> FileInfo:
        """Get file info.
        
        Args:
            path: File path
            
        Returns:
            FileInfo object
        """
        full_path = os.path.join(self.base_path, path)
        stat = os.stat(full_path)
        
        # Calculate hash
        hash_obj = hashlib.md5()
        if os.path.isfile(full_path):
            with open(full_path, "rb") as f:
                hash_obj.update(f.read())
        
        return FileInfo(
            path=path,
            name=os.path.basename(path),
            size=stat.st_size,
            created_at=datetime.fromtimestamp(stat.st_ctime).isoformat(),
            modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            hash=hash_obj.hexdigest(),
            is_directory=os.path.isdir(full_path),
        )

    def list_dir(self, path: str = ".") -> List[FileInfo]:
        """List directory contents.
        
        Args:
            path: Directory path
            
        Returns:
            List of FileInfo objects
        """
        full_path = os.path.join(self.base_path, path)
        items = []
        
        for item in os.listdir(full_path):
            item_path = os.path.join(path, item) if path != "." else item
            items.append(self.get_info(item_path))
        
        return items
