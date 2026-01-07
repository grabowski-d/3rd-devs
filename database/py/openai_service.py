"""OpenAI API wrapper with tokenization and embedding support."""
import os
from typing import Optional, Union, AsyncIterator, Dict, Any, List
from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessageParam
import tiktoken


class OpenAIService:
    """Service for OpenAI API interactions."""

    # Special tokens for formatting
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
        self.async_client = AsyncOpenAI(api_key=self.api_key)
        self.tokenizers: Dict[str, Any] = {}

    def _get_tokenizer(self, model: str) -> Any:
        """Get or create tokenizer for model.
        
        Args:
            model: Model name.
        
        Returns:
            Tiktoken encoder.
        """
        if model not in self.tokenizers:
            try:
                self.tokenizers[model] = tiktoken.encoding_for_model(model)
            except KeyError:
                # Fallback to cl100k_base
                self.tokenizers[model] = tiktoken.get_encoding('cl100k_base')
        return self.tokenizers[model]

    async def count_tokens(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = 'gpt-4o'
    ) -> int:
        """Count tokens in messages.
        
        Args:
            messages: List of chat completion messages.
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

    async def completion(
        self,
        config: Dict[str, Any]
    ) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        """Generate a chat completion.
        
        Args:
            config: Configuration dict with:
                - messages: List of ChatCompletionMessageParam
                - model: Model name (default: 'gpt-4o')
                - stream: Whether to stream (default: False)
                - temperature: Temperature (default: 0)
                - jsonMode: Use JSON mode (default: False)
                - maxTokens: Max tokens (default: 4096)
        
        Returns:
            ChatCompletion or async iterator of chunks if streaming.
        """
        messages = config.get('messages', [])
        model = config.get('model', 'gpt-4o')
        stream = config.get('stream', False)
        temperature = config.get('temperature', 0)
        json_mode = config.get('jsonMode', False)
        max_tokens = config.get('maxTokens', 4096)

        try:
            completion = self.client.chat.completions.create(
                messages=messages,
                model=model,
                stream=stream,
                temperature=temperature,
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

    def is_stream_response(
        self,
        response: Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]
    ) -> bool:
        """Check if response is a stream.
        
        Args:
            response: Response object.
        
        Returns:
            True if response is streaming.
        """
        return hasattr(response, '__aiter__') or hasattr(response, '__iter__')

    def parse_json_response(self, response: ChatCompletion) -> Dict[str, Any]:
        """Parse JSON from chat completion response.
        
        Args:
            response: ChatCompletion response.
        
        Returns:
            Parsed JSON dict, or error dict if parsing fails.
        """
        import json
        try:
            content = response.choices[0].message.content
            if not content:
                raise ValueError('No content in response')
            return json.loads(content)
        except Exception as error:
            return {'error': 'Failed to process response', 'result': False}

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
                input=text
            )
            return response.data[0].embedding
        except Exception as error:
            raise ValueError(f'Error creating embedding: {error}')
