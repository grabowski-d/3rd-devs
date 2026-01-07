"""OpenAI service for embeddings and completions with tokenization."""
import os
from typing import List, Union, Optional, AsyncIterator, Dict, Any
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessageParam
import tiktoken
import httpx


class OpenAIService:
    """OpenAI API wrapper with embedding and tokenization support."""

    # Special tokens for formatting
    IM_START = '<|im_start|>'
    IM_END = '<|im_end|>'
    IM_SEP = '<|im_sep|>'

    def __init__(self, api_key: Optional[str] = None, jina_api_key: Optional[str] = None):
        """Initialize OpenAI service.
        
        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var.
            jina_api_key: Jina API key. If not provided, uses JINA_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.jina_api_key = jina_api_key or os.getenv('JINA_API_KEY')
        self.client = OpenAI(api_key=self.api_key)
        self.tokenizers: Dict[str, Any] = {}

    def _get_tokenizer(self, model_name: str) -> Any:
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
                # Fallback to cl100k_base
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
            formatted_content += f'{self.IM_START}{role}{self.IM_SEP}{content}{self.IM_END}'
        
        formatted_content += f'{self.IM_START}assistant{self.IM_SEP}'
        
        tokens = tokenizer.encode(formatted_content)
        return len(tokens)

    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text using OpenAI.
        
        Args:
            text: Text to embed.
        
        Returns:
            Embedding vector.
        """
        try:
            response = self.client.embeddings.create(
                model='text-embedding-3-large',
                input=text,
            )
            return response.data[0].embedding
        except Exception as error:
            raise ValueError(f'Error creating embedding: {error}')

    async def create_jina_embedding(self, text: str) -> List[float]:
        """Create embedding for text using Jina API.
        
        Args:
            text: Text to embed.
        
        Returns:
            Embedding vector.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    'https://api.jina.ai/v1/embeddings',
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.jina_api_key}'
                    },
                    json={
                        'model': 'jina-embeddings-v3',
                        'task': 'text-matching',
                        'dimensions': 1024,
                        'late_chunking': False,
                        'embedding_type': 'float',
                        'input': [text]
                    }
                )

                if response.status_code != 200:
                    raise ValueError(f'HTTP error! status: {response.status_code}')

                data = response.json()
                return data['data'][0]['embedding']
        except Exception as error:
            raise ValueError(f'Error creating Jina embedding: {error}')

    async def completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = 'gpt-4o',
        stream: bool = False,
        json_mode: bool = False,
        max_tokens: int = 4096
    ) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        """Generate a chat completion.
        
        Args:
            messages: List of chat messages.
            model: Model name (default: gpt-4o).
            stream: Whether to stream (default: False).
            json_mode: Use JSON mode (default: False).
            max_tokens: Max tokens (default: 4096).
        
        Returns:
            ChatCompletion or async iterator of chunks if streaming.
        """
        try:
            # o1 models don't support stream, temperature, etc.
            if model in ['o1-mini', 'o1-preview']:
                completion = self.client.chat.completions.create(
                    messages=messages,
                    model=model,
                )
            else:
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
        """Calculate token cost for image.
        
        Args:
            width: Image width in pixels.
            height: Image height in pixels.
            detail: Detail level ('low' or 'high').
        
        Returns:
            Token cost.
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
