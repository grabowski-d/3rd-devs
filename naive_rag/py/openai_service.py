"""OpenAI service for RAG - embeddings and completions."""
import os
from typing import List, Union, Optional, AsyncIterator
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessageParam
import tiktoken


class OpenAIService:
    """OpenAI API wrapper for RAG system."""

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
        """Get or create tokenizer.
        
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
        """Count tokens in messages."""
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
        """Create embedding for text.
        
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

    async def completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = 'gpt-4o',
        stream: bool = False,
        json_mode: bool = False,
        max_tokens: int = 4096
    ) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        """Generate chat completion."""
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
