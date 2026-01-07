"""Text splitting and document processing service."""
import re
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import tiktoken


@dataclass
class IDoc:
    """Document with metadata."""
    text: str
    metadata: Dict[str, Any]


class TextSplitter:
    """Service for splitting text into chunks with token awareness."""

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
        """Initialize tokenizer for model.
        
        Args:
            model: Optional model name. If provided, switches model.
        """
        if model and model != self.model_name:
            self.model_name = model
            self.tokenizer = None
        
        if self.tokenizer is None:
            try:
                self.tokenizer = tiktoken.encoding_for_model(self.model_name)
            except KeyError:
                self.tokenizer = tiktoken.get_encoding('cl100k_base')

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text.
        
        Args:
            text: Text to count tokens for.
        
        Returns:
            Token count.
        """
        if self.tokenizer is None:
            raise ValueError('Tokenizer not initialized')
        
        formatted_content = self._format_for_tokenization(text)
        tokens = self.tokenizer.encode(formatted_content)
        return len(tokens)

    def _format_for_tokenization(self, text: str) -> str:
        """Format text for tokenization.
        
        Args:
            text: Text to format.
        
        Returns:
            Formatted text with special tokens.
        """
        return f"<|im_start|>user\n{text}<|im_end|>\n<|im_start|>assistant<|im_end|>"

    async def split(self, text: str, limit: int) -> List[IDoc]:
        """Split text into chunks respecting token limit.
        
        Args:
            text: Text to split.
            limit: Token limit per chunk.
        
        Returns:
            List of document chunks.
        """
        self._initialize_tokenizer()
        print(f'Starting split process with limit: {limit} tokens')
        
        chunks: List[IDoc] = []
        position = 0
        total_length = len(text)
        current_headers: Dict[str, List[str]] = {}

        while position < total_length:
            print(f'Processing chunk starting at position: {position}')
            chunk_text, chunk_end = self._get_chunk(text, position, limit)
            tokens = self._count_tokens(chunk_text)
            print(f'Chunk tokens: {tokens}')

            headers_in_chunk = self._extract_headers(chunk_text)
            self._update_current_headers(current_headers, headers_in_chunk)

            content, urls, images = self._extract_urls_and_images(chunk_text)

            chunks.append(IDoc(
                text=content,
                metadata={
                    'tokens': tokens,
                    'headers': dict(current_headers),
                    'urls': urls,
                    'images': images,
                }
            ))

            print(f'Chunk processed. New position: {chunk_end}')
            position = chunk_end

        print(f'Split process completed. Total chunks: {len(chunks)}')
        return chunks

    def _get_chunk(self, text: str, start: int, limit: int) -> Tuple[str, int]:
        """Get next chunk respecting token limit.
        
        Args:
            text: Full text.
            start: Start position.
            limit: Token limit.
        
        Returns:
            Tuple of (chunk_text, chunk_end_position).
        """
        print(f'Getting chunk starting at {start} with limit {limit}')
        
        # Estimate end position
        remaining_text = text[start:]
        if len(remaining_text) == 0:
            return '', start
        
        # Conservative estimate: rough characters per token ratio
        chars_per_token = len(remaining_text) / self._count_tokens(remaining_text)
        estimated_end = start + int(limit * chars_per_token * 0.9)  # 90% to be safe
        estimated_end = min(estimated_end, len(text))
        
        chunk_text = text[start:estimated_end]
        tokens = self._count_tokens(chunk_text)
        
        # Adjust if over limit
        while tokens > limit and estimated_end > start:
            print(f'Chunk exceeds limit with {tokens} tokens. Adjusting end position...')
            estimated_end = self._find_new_chunk_end(text, start, estimated_end)
            chunk_text = text[start:estimated_end]
            tokens = self._count_tokens(chunk_text)
        
        # Align with newlines
        estimated_end = self._adjust_chunk_end(text, start, estimated_end, tokens, limit)
        chunk_text = text[start:estimated_end]
        tokens = self._count_tokens(chunk_text)
        print(f'Final chunk end: {estimated_end}')
        
        return chunk_text, estimated_end

    def _adjust_chunk_end(self, text: str, start: int, end: int, current_tokens: int, limit: int) -> int:
        """Adjust chunk end to align with newlines.
        
        Args:
            text: Full text.
            start: Chunk start.
            end: Current end.
            current_tokens: Current token count.
            limit: Token limit.
        
        Returns:
            Adjusted end position.
        """
        min_chunk_tokens = limit * 0.8  # Minimum 80% of limit

        # Try extending to next newline
        next_newline = text.find('\n', end)
        if next_newline != -1 and next_newline < len(text):
            extended_end = next_newline + 1
            chunk_text = text[start:extended_end]
            tokens = self._count_tokens(chunk_text)
            if tokens <= limit and tokens >= min_chunk_tokens:
                print(f'Extending chunk to next newline at position {extended_end}')
                return extended_end

        # Try reducing to previous newline
        prev_newline = text.rfind('\n', start, end)
        if prev_newline > start:
            reduced_end = prev_newline + 1
            chunk_text = text[start:reduced_end]
            tokens = self._count_tokens(chunk_text)
            if tokens <= limit and tokens >= min_chunk_tokens:
                print(f'Reducing chunk to previous newline at position {reduced_end}')
                return reduced_end

        return end

    def _find_new_chunk_end(self, text: str, start: int, end: int) -> int:
        """Find new chunk end by reducing by 10%.
        
        Args:
            text: Full text.
            start: Chunk start.
            end: Current end.
        
        Returns:
            New end position.
        """
        new_end = end - max(1, (end - start) // 10)
        if new_end <= start:
            new_end = start + 1
        return new_end

    def _extract_headers(self, text: str) -> Dict[str, List[str]]:
        """Extract markdown headers from text.
        
        Args:
            text: Text to extract from.
        
        Returns:
            Dict mapping header level (h1-h6) to list of headers.
        """
        headers: Dict[str, List[str]] = {}
        header_regex = r'^(#{1,6})\s+(.*)$'
        
        for match in re.finditer(header_regex, text, re.MULTILINE):
            level = len(match.group(1))
            content = match.group(2).strip()
            key = f'h{level}'
            if key not in headers:
                headers[key] = []
            headers[key].append(content)

        return headers

    def _update_current_headers(self, current: Dict[str, List[str]], extracted: Dict[str, List[str]]) -> None:
        """Update current headers with extracted headers.
        
        Args:
            current: Current headers dict (modified in place).
            extracted: Extracted headers dict.
        """
        for level in range(1, 7):
            key = f'h{level}'
            if key in extracted:
                current[key] = extracted[key]
                self._clear_lower_headers(current, level)

    def _clear_lower_headers(self, headers: Dict[str, List[str]], level: int) -> None:
        """Clear headers below given level.
        
        Args:
            headers: Headers dict (modified in place).
            level: Header level threshold.
        """
        for l in range(level + 1, 7):
            headers.pop(f'h{l}', None)

    def _extract_urls_and_images(self, text: str) -> Tuple[str, List[str], List[str]]:
        """Extract and replace URLs and images in text.
        
        Args:
            text: Text to process.
        
        Returns:
            Tuple of (processed_text, urls, images).
        """
        urls: List[str] = []
        images: List[str] = []
        url_index = 0
        image_index = 0

        # Extract images: ![alt](url)
        def replace_image(match):
            nonlocal image_index
            alt_text = match.group(1)
            url = match.group(2)
            images.append(url)
            replacement = f'![{alt_text}]({{{{$img{image_index}}}}})'  
            image_index += 1
            return replacement

        # Extract links: [text](url)
        def replace_url(match):
            nonlocal url_index
            link_text = match.group(1)
            url = match.group(2)
            urls.append(url)
            replacement = f'[{link_text}]({{{{$url{url_index}}}}})'  
            url_index += 1
            return replacement

        content = re.sub(r'!\[([^\]]*)]\(([^)]+)\)', replace_image, text)
        content = re.sub(r'\[([^\]]+)]\(([^)]+)\)', replace_url, content)

        return content, urls, images

    async def document(
        self,
        text: str,
        model: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> IDoc:
        """Create a document from text with metadata.
        
        Args:
            text: Text content.
            model: Optional model name for tokenization.
            additional_metadata: Optional additional metadata.
        
        Returns:
            Document with metadata.
        """
        self._initialize_tokenizer(model)
        tokens = self._count_tokens(text)
        headers = self._extract_headers(text)
        content, urls, images = self._extract_urls_and_images(text)
        
        metadata = {
            'tokens': tokens,
            'headers': headers,
            'urls': urls,
            'images': images,
        }
        if additional_metadata:
            metadata.update(additional_metadata)

        return IDoc(text=content, metadata=metadata)
