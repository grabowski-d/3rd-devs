"""Text Splitter Service - Python implementation of embedding/TextService.ts"""
import re
from typing import Dict, List, Any
from dataclasses import dataclass, field
import tiktoken

@dataclass
class IDoc:
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class TextSplitter:
    SPECIAL_TOKENS = {
        '<|im_start|>': 100264,
        '<|im_end|>': 100265,
        '<|im_sep|>': 100266,
    }
    
    def __init__(self, model_name: str = 'gpt-4'):
        self.model_name = model_name
        self.tokenizer = None
    
    async def _initialize_tokenizer(self, model: str = None) -> None:
        if model:
            self.model_name = model
        if not self.tokenizer:
            try:
                self.tokenizer = tiktoken.encoding_for_model(self.model_name)
            except KeyError:
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def _count_tokens(self, text: str) -> int:
        if not self.tokenizer:
            raise Exception('Tokenizer not initialized')
        formatted = self._format_for_tokenization(text)
        tokens = self.tokenizer.encode(formatted)
        return len(tokens)
    
    def _format_for_tokenization(self, text: str) -> str:
        return f"<|im_start|>user\n{text}<|im_end|>\n<|im_start|>assistant<|im_end|>"
    
    async def split(self, text: str, limit: int) -> List[IDoc]:
        print(f"Starting split process with limit: {limit} tokens")
        await self._initialize_tokenizer()
        chunks: List[IDoc] = []
        position = 0
        total_length = len(text)
        current_headers: Dict[str, List[str]] = {}
        
        while position < total_length:
            print(f"Processing chunk starting at position: {position}")
            chunk_text, chunk_end = self._get_chunk(text, position, limit)
            tokens = self._count_tokens(chunk_text)
            print(f"Chunk tokens: {tokens}")
            
            headers_in_chunk = self._extract_headers(chunk_text)
            self._update_current_headers(current_headers, headers_in_chunk)
            content, urls, images = self._extract_urls_and_images(chunk_text)
            
            chunks.append(IDoc(
                text=content,
                metadata={
                    'tokens': tokens,
                    'headers': current_headers.copy(),
                    'urls': urls,
                    'images': images,
                }
            ))
            
            print(f"Chunk processed. New position: {chunk_end}")
            position = chunk_end
        
        print(f"Split process completed. Total chunks: {len(chunks)}")
        return chunks
    
    def _get_chunk(self, text: str, start: int, limit: int) -> tuple:
        print(f"Getting chunk starting at {start} with limit {limit}")
        end = min(start + int((len(text) - start) * limit / max(1, self._count_tokens(text[start:]))), len(text))
        
        chunk_text = text[start:end]
        tokens = self._count_tokens(chunk_text)
        
        while tokens > limit and end > start:
            print(f"Chunk exceeds limit with {tokens} tokens. Adjusting...")
            end = self._find_new_chunk_end(text, start, end)
            chunk_text = text[start:end]
            tokens = self._count_tokens(chunk_text)
        
        end = self._adjust_chunk_end(text, start, end, tokens, limit)
        chunk_text = text[start:end]
        tokens = self._count_tokens(chunk_text)
        print(f"Final chunk end: {end}")
        return chunk_text, end
    
    def _adjust_chunk_end(self, text: str, start: int, end: int, current_tokens: int, limit: int) -> int:
        min_chunk_tokens = limit * 0.8
        next_newline = text.find('\n', end)
        prev_newline = text.rfind('\n', start, end)
        
        if next_newline != -1 and next_newline < len(text):
            extended_end = next_newline + 1
            chunk_text = text[start:extended_end]
            tokens = self._count_tokens(chunk_text)
            if tokens <= limit and tokens >= min_chunk_tokens:
                print(f"Extending chunk to next newline at position {extended_end}")
                return extended_end
        
        if prev_newline > start:
            reduced_end = prev_newline + 1
            chunk_text = text[start:reduced_end]
            tokens = self._count_tokens(chunk_text)
            if tokens <= limit and tokens >= min_chunk_tokens:
                print(f"Reducing chunk to previous newline at position {reduced_end}")
                return reduced_end
        
        return end
    
    def _find_new_chunk_end(self, text: str, start: int, end: int) -> int:
        new_end = end - int((end - start) / 10)
        return max(start + 1, new_end)
    
    def _extract_headers(self, text: str) -> Dict[str, List[str]]:
        headers: Dict[str, List[str]] = {}
        header_regex = r'(^|\n)(#{1,6})\s+(.*?)(?=\n|$)'
        for match in re.finditer(header_regex, text, re.MULTILINE):
            level = len(match.group(2))
            content = match.group(3).strip()
            key = f'h{level}'
            if key not in headers:
                headers[key] = []
            headers[key].append(content)
        return headers
    
    def _update_current_headers(self, current: Dict[str, List[str]], extracted: Dict[str, List[str]]) -> None:
        for level in range(1, 7):
            key = f'h{level}'
            if key in extracted:
                current[key] = extracted[key]
                self._clear_lower_headers(current, level)
    
    def _clear_lower_headers(self, headers: Dict[str, List[str]], level: int) -> None:
        for l in range(level + 1, 7):
            headers.pop(f'h{l}', None)
    
    def _extract_urls_and_images(self, text: str) -> tuple:
        urls: List[str] = []
        images: List[str] = []
        url_index = 0
        image_index = 0
        
        content = re.sub(
            r'!\[([^\]]*)\]\(([^)]+)\)',
            lambda m: (images.append(m.group(2)) or f"![{m.group(1)}]({{{{'$img' + str(image_index-1)}}}})")
            if (image_index := image_index + 1) else "",
            text
        )
        
        # Better approach without lambda with side effects
        def replace_images(match):
            images.append(match.group(2))
            return f"![{match.group(1)}]({{{{$img{len(images)-1}}}})"
        
        content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_images, text)
        
        def replace_urls(match):
            urls.append(match.group(2))
            return f"[{match.group(1)}]({{{{$url{len(urls)-1}}}})"
        
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_urls, content)
        
        return content, urls, images
    
    async def document(self, text: str, model: str = None, additional_metadata: Dict[str, Any] = None) -> IDoc:
        await self._initialize_tokenizer(model)
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
