"""Text processing for RAG system."""
import re
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import tiktoken


@dataclass
class IDoc:
    """Document with metadata."""
    text: str
    metadata: Dict[str, Any]


class TextSplitter:
    """Text splitter for RAG with token awareness."""

    SPECIAL_TOKENS = {
        '<|im_start|>': 100264,
        '<|im_end|>': 100265,
        '<|im_sep|>': 100266,
    }

    def __init__(self, model_name: str = 'gpt-4'):
        """Initialize text splitter.
        
        Args:
            model_name: Model name for tokenization.
        """
        self.model_name = model_name
        self.tokenizer: Optional[Any] = None

    def _initialize_tokenizer(self, model: Optional[str] = None) -> None:
        """Initialize tokenizer."""
        if model and model != self.model_name:
            self.model_name = model
            self.tokenizer = None
        
        if self.tokenizer is None:
            try:
                self.tokenizer = tiktoken.encoding_for_model(self.model_name)
            except KeyError:
                self.tokenizer = tiktoken.get_encoding('cl100k_base')

    def _count_tokens(self, text: str) -> int:
        """Count tokens."""
        if self.tokenizer is None:
            raise ValueError('Tokenizer not initialized')
        
        formatted = f"<|im_start|>user\n{text}<|im_end|>\n<|im_start|>assistant<|im_end|>"
        return len(self.tokenizer.encode(formatted))

    async def document(
        self,
        text: str,
        model: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> IDoc:
        """Create document from text.
        
        Args:
            text: Text content.
            model: Optional model name.
            additional_metadata: Optional additional metadata.
        
        Returns:
            Document with metadata.
        """
        self._initialize_tokenizer(model)
        tokens = self._count_tokens(text)
        
        metadata = {
            'tokens': tokens,
        }
        if additional_metadata:
            metadata.update(additional_metadata)

        return IDoc(text=text, metadata=metadata)
