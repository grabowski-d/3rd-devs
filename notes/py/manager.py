"""Notes manager."""
from typing import List, Dict
class NotesManager:
    def __init__(self):
        self.notes: List[Dict] = []
    def add_note(self, title: str, content: str) -> None:
        self.notes.append({'title': title, 'content': content})
    def get_notes(self) -> List[Dict]:
        return self.notes
