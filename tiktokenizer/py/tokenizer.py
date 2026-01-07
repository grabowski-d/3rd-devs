"""Token counter."""
import tiktoken
from typing import List, Dict
class TokenCounter:
    def __init__(self, model: str = 'gpt-4'):
        self.tokenizer = tiktoken.encoding_for_model(model)
    def count(self, text: str) -> int:
        return len(self.tokenizer.encode(text))
    def count_messages(self, messages: List[Dict[str, str]]) -> int:
        return sum(self.count(msg.get('content', '')) for msg in messages)
