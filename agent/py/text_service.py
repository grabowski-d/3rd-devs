"""Text processing service with tokenization and chunking."""
import re
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field
import tiktoken
import uuid


@dataclass
class DocumentMetadata:
    """Metadata for a document chunk."""
    tokens: int
    headers: Dict[str, List[str]] = field(default_factory=dict)
    urls: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    type: str = 'text'
    content_type: str = 'chunk'  # 'chunk' or 'complete'
    source: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    mime_type: Optional[str] = None
    conversation_uuid: Optional[str] = None
    uuid: Optional[str] = None
    additional: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IDoc:
    """Document structure."""
    text: str
    metadata: DocumentMetadata


class TextService:
    """Service for text processing, chunking, and tokenization."""

    SPECIAL_TOKENS = {
        '<|im_start|>': 100264,
        '<|im_end|>': 100265,
        '<|im_sep|>': 100266,
    }

    def __init__(self, model_name: str = 'gpt-4o'):
        """Initialize text service.
        
        Args:
            model_name: OpenAI model name for tokenization.
        """
        self.model_name = model_name
        self.tokenizer = None
        self._init_tokenizer()

    def _init_tokenizer(self) -> None:
        """Initialize tiktoken tokenizer."""
        try:
            self.tokenizer = tiktoken.encoding_for_model(self.model_name)
        except Exception:
            # Fallback to cl100k_base encoding
            self.tokenizer = tiktoken.get_encoding('cl100k_base')

    def _format_for_tokenization(self, text: str) -> str:
        """Format text for tokenization with special tokens."""
        return f'<|im_start|>user\n{text}<|im_end|>\n<|im_start|>assistant<|im_end|>'

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if not self.tokenizer:
            raise ValueError('Tokenizer not initialized')
        formatted = self._format_for_tokenization(text)
        tokens = self.tokenizer.encode(formatted)
        return len(tokens)

    def _get_chunk(
        self,
        text: str,
        start: int,
        limit: int
    ) -> Tuple[str, int]:
        """Get a chunk of text within token limit.
        
        Args:
            text: Full text to chunk.
            start: Start position.
            limit: Token limit for chunk.
        
        Returns:
            Tuple of (chunk_text, chunk_end_position)
        """
        # Calculate overhead from formatting
        overhead = self._count_tokens(self._format_for_tokenization('')) - self._count_tokens('')

        # Estimate end position
        if start < len(text):
            remaining = len(text) - start
            ratio = limit / max(self._count_tokens(text[start:]), 1)
            end = min(start + int(remaining * ratio), len(text))
        else:
            end = len(text)

        # Adjust to fit within token limit
        chunk_text = text[start:end]
        tokens = self._count_tokens(chunk_text)

        while tokens + overhead > limit and end > start:
            end = start + int((end - start) * 0.9)  # Reduce by 10%
            chunk_text = text[start:end]
            tokens = self._count_tokens(chunk_text)

        # Align with newlines
        end = self._adjust_chunk_end(text, start, end, tokens + overhead, limit)

        chunk_text = text[start:end]
        return chunk_text, end

    def _adjust_chunk_end(
        self,
        text: str,
        start: int,
        end: int,
        current_tokens: int,
        limit: int
    ) -> int:
        """Adjust chunk end to align with newlines."""
        min_chunk_tokens = limit * 0.8

        # Try extending to next newline
        next_newline = text.find('\n', end)
        if next_newline != -1 and next_newline < len(text):
            extended_end = next_newline + 1
            tokens = self._count_tokens(text[start:extended_end])
            if tokens <= limit and tokens >= min_chunk_tokens:
                return extended_end

        # Try reducing to previous newline
        prev_newline = text.rfind('\n', start, end)
        if prev_newline > start:
            reduced_end = prev_newline + 1
            tokens = self._count_tokens(text[start:reduced_end])
            if tokens <= limit and tokens >= min_chunk_tokens:
                return reduced_end

        return end

    def _extract_headers(self, text: str) -> Dict[str, List[str]]:
        """Extract markdown headers from text."""
        headers: Dict[str, List[str]] = {}
        # Match # to ###### headers
        pattern = r'^(#{1,6})\s+(.+)$'
        for match in re.finditer(pattern, text, re.MULTILINE):
            level = len(match.group(1))
            content = match.group(2).strip()
            key = f'h{level}'
            if key not in headers:
                headers[key] = []
            headers[key].append(content)
        return headers

    def _update_current_headers(
        self,
        current: Dict[str, List[str]],
        extracted: Dict[str, List[str]]
    ) -> None:
        """Update current headers tracking."""
        for level in range(1, 7):
            key = f'h{level}'
            if key in extracted:
                current[key] = extracted[key]
                # Clear lower level headers
                for l in range(level + 1, 7):
                    current.pop(f'h{l}', None)

    def _extract_urls_and_images(self, text: str) -> Tuple[str, List[str], List[str]]:
        """Extract URLs and images from markdown.
        
        Returns:
            Tuple of (content_with_placeholders, urls, images)
        """
        urls: List[str] = []
        images: List[str] = []
        url_index = 0
        image_index = 0

        # Extract image markdown: ![alt](url)
        def replace_image(match):
            nonlocal image_index
            images.append(match.group(2))
            result = f'![{match.group(1)}]({{{{$img{image_index}}}}})'  
            image_index += 1
            return result

        content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, text)

        # Extract link markdown: [text](url)
        def replace_link(match):
            nonlocal url_index
            link_url = match.group(2)
            if not link_url.startswith('{{$img'):
                urls.append(link_url)
                result = f'[{match.group(1)}]({{{{$url{url_index}}}}})'  
                url_index += 1
                return result
            return match.group(0)

        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, content)

        return content, urls, images

    async def split(
        self,
        text: str,
        limit: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[IDoc]:
        """Split text into chunks with token limit.
        
        Args:
            text: Text to split.
            limit: Token limit per chunk.
            metadata: Additional metadata to include.
        
        Returns:
            List of IDoc chunks.
        """
        position = 0
        chunks: List[IDoc] = []
        current_headers: Dict[str, List[str]] = {}

        while position < len(text):
            chunk_text, position = self._get_chunk(text, position, limit)

            tokens = self._count_tokens(chunk_text)
            headers_in_chunk = self._extract_headers(chunk_text)
            self._update_current_headers(current_headers, headers_in_chunk)

            content, urls, images = self._extract_urls_and_images(chunk_text)

            doc_metadata = DocumentMetadata(
                tokens=tokens,
                headers=current_headers.copy(),
                urls=urls,
                images=images,
                type=metadata.get('type', 'text') if metadata else 'text',
                content_type=metadata.get('content_type', 'chunk') if metadata else 'chunk',
                source=metadata.get('source') if metadata else None,
                name=metadata.get('name') if metadata else None,
                description=metadata.get('description') if metadata else None,
                mime_type=metadata.get('mime_type') if metadata else None,
                conversation_uuid=metadata.get('conversation_uuid') if metadata else None,
                uuid=metadata.get('uuid', str(uuid.uuid4())) if metadata else str(uuid.uuid4()),
                additional=metadata.get('additional', {}) if metadata else {},
            )

            chunks.append(IDoc(text=content, metadata=doc_metadata))

        return chunks

    async def document(
        self,
        content: str,
        model_name: Optional[str] = None,
        metadata_overrides: Optional[Dict[str, Any]] = None
    ) -> IDoc:
        """Create a single document.
        
        Args:
            content: Document content.
            model_name: Optional model name override.
            metadata_overrides: Optional metadata overrides.
        
        Returns:
            IDoc document.
        """
        if model_name and model_name != self.model_name:
            self.model_name = model_name
            self._init_tokenizer()

        overrides = metadata_overrides or {}
        tokens = self._count_tokens(content)

        doc_metadata = DocumentMetadata(
            tokens=tokens,
            type=overrides.get('type', 'text'),
            content_type=overrides.get('content_type', 'complete'),
            source=overrides.get('source', 'generated'),
            name=overrides.get('name', 'Generated Document'),
            mime_type=overrides.get('mime_type', 'text/plain'),
            conversation_uuid=overrides.get('conversation_uuid'),
            uuid=overrides.get('uuid', str(uuid.uuid4())),
            additional=overrides.get('additional', {}),
        )

        return IDoc(text=content, metadata=doc_metadata)

    def restore_placeholders(self, doc: IDoc) -> IDoc:
        """Restore URL and image placeholders in document.
        
        Args:
            doc: Document with placeholders.
        
        Returns:
            Document with restored URLs/images.
        """
        text = doc.text
        metadata = doc.metadata

        # Restore image placeholders
        if metadata.images:
            for idx, url in enumerate(metadata.images):
                pattern = f'!\\[([^\\]]*)\\](\\{{{{\\$img{idx}\\}}}})'
                text = re.sub(pattern, f'![\\1]({url})', text)

        # Restore URL placeholders
        if metadata.urls:
            for idx, url in enumerate(metadata.urls):
                pattern = f'\\[([^\\]]*)\\](\\{{{{\\$url{idx}\\}}}})'
                text = re.sub(
                    pattern,
                    lambda m: f'[{m.group(1).replace("_", "\\_")}]({url})',
                    text
                )

        return IDoc(text=text, metadata=metadata)
