"""Text service for agent."""
import tiktoken
from typing import Dict, Any, Optional
from uuid import uuid4
from .types import IDoc


class TextService:
    """Text service for document creation."""
    
    def __init__(self, model_name: str = 'gpt-4o'):
        self.model_name = model_name
        self.tokenizer: Optional[Any] = None
    
    def _initialize_tokenizer(self) -> None:
        if self.tokenizer is None:
            try:
                self.tokenizer = tiktoken.encoding_for_model(self.model_name)
            except KeyError:
                self.tokenizer = tiktoken.get_encoding('cl100k_base')
    
    async def document(
        self,
        text: str,
        name: str,
        description: str,
        doc_type: str,
        content_type: str,
        source: str,
        conversation_uuid: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> IDoc:
        """Create document.
        
        Args:
            text: Document text.
            name: Document name.
            description: Document description.
            doc_type: Document type.
            content_type: Content type (complete or chunk).
            source: Source URL or identifier.
            conversation_uuid: Conversation UUID.
            metadata: Optional additional metadata.
        
        Returns:
            Document object.
        """
        return IDoc(
            uuid=str(uuid4()),
            name=name,
            description=description,
            type=doc_type,
            content_type=content_type,
            source=source,
            conversation_uuid=conversation_uuid,
            text=text
        )
