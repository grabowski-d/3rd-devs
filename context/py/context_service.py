"""Context service for document retrieval and insertion."""

import re
import uuid
from typing import Dict, List, Optional
from openai.types.chat import ChatCompletionMessageParam

from .openai_service import OpenAIService


class ContextService:
    """Service for managing document context with placeholder insertion."""

    def __init__(self, openai_service: OpenAIService):
        """Initialize context service.

        Args:
            openai_service: OpenAI service instance.
        """
        self.openai_service = openai_service
        self.documents: Dict[str, str] = {}
        self.document_metadata: Dict[str, Dict[str, str]] = {}

    def add_document(
        self,
        content: str,
        title: str,
        doc_uuid: Optional[str] = None,
    ) -> str:
        """Add document to context store.

        Args:
            content: Document content.
            title: Document title.
            doc_uuid: Optional UUID. Generated if not provided.

        Returns:
            Document UUID.
        """
        doc_uuid = doc_uuid or str(uuid.uuid4())
        self.documents[doc_uuid] = content
        self.document_metadata[doc_uuid] = {"title": title}
        return doc_uuid

    def get_document(self, doc_uuid: str) -> Optional[str]:
        """Get document by UUID.

        Args:
            doc_uuid: Document UUID.

        Returns:
            Document content or None.
        """
        return self.documents.get(doc_uuid)

    def list_documents(self) -> List[Dict[str, str]]:
        """List all documents.

        Returns:
            List of document metadata with UUIDs.
        """
        return [
            {"uuid": uuid_key, **metadata}
            for uuid_key, metadata in self.document_metadata.items()
        ]

    def create_system_prompt(self) -> str:
        """Create system prompt with available documents.

        Returns:
            System prompt with document list.
        """
        doc_list = "\n".join(
            f"  - {metadata['title']}: {doc_uuid}"
            for doc_uuid, metadata in self.document_metadata.items()
        )

        return f"""As an AI assistant, you can use the following documents in your responses 
by referencing them with the placeholder: [[uuid]] (double square brackets).

<rule>
- Placeholder is double square brackets. Make sure to use it correctly.
- Documents are long forms of text, so use them naturally within the text.
- Format: "here's your content: \n\n [[uuid]] \n\n".
</rule>

<available_documents>
{doc_list or "No documents available"}
</available_documents>"""

    async def query(
        self,
        query: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Query documents with context.

        Args:
            query: User query.
            system_prompt: Optional custom system prompt.

        Returns:
            Response with document placeholders replaced.
        """
        system = system_prompt or self.create_system_prompt()

        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": system},
            {"role": "user", "content": query},
        ]

        completion = await self.openai_service.completion(
            messages=messages,
        )

        answer = completion.choices[0].message.content or ""

        # Replace placeholders with actual documents
        def replace_placeholder(match) -> str:
            doc_uuid = match.group(1)
            return self.documents.get(doc_uuid, match.group(0))

        answer = re.sub(r"\[\[([^\]]+)\]\]", replace_placeholder, answer)
        return answer

    def clear_documents(self) -> None:
        """Clear all documents."""
        self.documents.clear()
        self.document_metadata.clear()
