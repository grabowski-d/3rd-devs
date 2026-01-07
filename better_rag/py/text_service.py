"""Text service for better RAG."""
from dataclasses import dataclass
from typing import Dict, Any, Optional
import tiktoken

@dataclass
class IDoc:
    text: str
    metadata: Dict[str, Any]

class TextSplitter:
    def __init__(self, model_name: str = 'gpt-4'):
        self.model_name = model_name
        self.tokenizer: Optional[Any] = None
    
    def _initialize_tokenizer(self, model: Optional[str] = None) -> None:
        if model and model != self.model_name:
            self.model_name = model
            self.tokenizer = None
        if self.tokenizer is None:
            try:
                self.tokenizer = tiktoken.encoding_for_model(self.model_name)
            except KeyError:
                self.tokenizer = tiktoken.get_encoding('cl100k_base')
    
    async def document(self, text: str, model: Optional[str] = None, additional_metadata: Optional[Dict[str, Any]] = None) -> IDoc:
        self._initialize_tokenizer(model)
        metadata = {'tokens': len(self.tokenizer.encode(text)) if self.tokenizer else 0}
        if additional_metadata:
            metadata.update(additional_metadata)
        return IDoc(text=text, metadata=metadata)
