"""OpenAI service for vision and image analysis."""
import os
from typing import List, Union, Optional, AsyncIterator
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessageParam
import tiktoken


class OpenAIService:
    """OpenAI API wrapper with vision capabilities."""

    IM_START = '<|im_start|>'
    IM_END = '<|im_end|>'
    IM_SEP = '<|im_sep|>'

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI service.
        
        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)
        self.tokenizers = {}

    def _get_tokenizer(self, model_name: str):
        """Get or create tokenizer for model.
        
        Args:
            model_name: Model name.
        
        Returns:
            Tiktoken encoder.
        """
        if model_name not in self.tokenizers:
            try:
                self.tokenizers[model_name] = tiktoken.encoding_for_model(model_name)
            except KeyError:
                self.tokenizers[model_name] = tiktoken.get_encoding('cl100k_base')
        return self.tokenizers[model_name]

    async def count_tokens(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = 'gpt-4o'
    ) -> int:
        """Count tokens in messages.
        
        Args:
            messages: List of chat messages.
            model: Model name for tokenization.
        
        Returns:
            Total token count.
        """
        tokenizer = self._get_tokenizer(model)
        
        formatted_content = ''
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            # Handle text content only for tokenization
            if isinstance(content, str):
                formatted_content += f'{self.IM_START}{role}{self.IM_SEP}{content}{self.IM_END}'
            elif isinstance(content, list):
                # Extract text from content parts
                text_parts = []
                for part in content:
                    if isinstance(part, dict) and part.get('type') == 'text':
                        text_parts.append(part.get('text', ''))
                formatted_content += f'{self.IM_START}{role}{self.IM_SEP}{"".join(text_parts)}{self.IM_END}'
        
        formatted_content += f'{self.IM_START}assistant{self.IM_SEP}'
        tokens = tokenizer.encode(formatted_content)
        return len(tokens)

    async def completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = 'gpt-4o',
        stream: bool = False,
        json_mode: bool = False,
        max_tokens: int = 1024
    ) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        """Generate a chat completion with vision support.
        
        Args:
            messages: List of chat messages (can include images).
            model: Model name (default: gpt-4o).
            stream: Whether to stream (default: False).
            json_mode: Use JSON mode (default: False).
            max_tokens: Max tokens (default: 1024).
        
        Returns:
            ChatCompletion or async iterator of chunks if streaming.
        """
        try:
            completion = self.client.chat.completions.create(
                messages=messages,
                model=model,
                stream=stream,
                max_tokens=max_tokens,
                response_format={
                    'type': 'json_object'
                } if json_mode else {'type': 'text'}
            )

            if stream:
                return completion
            else:
                return completion

        except Exception as error:
            raise ValueError(f'Error in OpenAI completion: {error}')

    async def calculate_image_tokens(
        self,
        width: int,
        height: int,
        detail: str = 'high'
    ) -> int:
        """Calculate token cost for image in vision tasks.
        
        Args:
            width: Image width in pixels.
            height: Image height in pixels.
            detail: Detail level ('low' or 'high').
        
        Returns:
            Token cost for the image.
        """
        token_cost = 0

        if detail == 'low':
            token_cost += 85
            return token_cost

        MAX_DIMENSION = 2048
        SCALE_SIZE = 768

        # Resize to fit within MAX_DIMENSION x MAX_DIMENSION
        if width > MAX_DIMENSION or height > MAX_DIMENSION:
            aspect_ratio = width / height
            if aspect_ratio > 1:
                width = MAX_DIMENSION
                height = int(MAX_DIMENSION / aspect_ratio)
            else:
                height = MAX_DIMENSION
                width = int(MAX_DIMENSION * aspect_ratio)

        # Scale the shortest side to SCALE_SIZE
        if width >= height and height > SCALE_SIZE:
            width = int((SCALE_SIZE / height) * width)
            height = SCALE_SIZE
        elif height > width and width > SCALE_SIZE:
            height = int((SCALE_SIZE / width) * height)
            width = SCALE_SIZE

        # Calculate the number of 512px squares
        num_squares = ((width + 511) // 512) * ((height + 511) // 512)

        # Calculate the token cost
        token_cost += (num_squares * 170) + 85

        return token_cost
