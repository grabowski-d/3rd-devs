"""File reader."""
import os
from typing import Optional
class FileReader:
    @staticmethod
    def read_file(path: str) -> Optional[str]:
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return f.read()
        except Exception as e:
            print(f"Error: {e}")
        return None
