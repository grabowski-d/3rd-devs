"""File handler."""
import os
from typing import List
class FileHandler:
    @staticmethod
    def list_files(directory: str) -> List[str]:
        try:
            return os.listdir(directory)
        except Exception as e:
            print(f"Error: {e}")
            return []
    @staticmethod
    def file_exists(path: str) -> bool:
        return os.path.exists(path)
