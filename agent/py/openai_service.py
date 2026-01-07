"""OpenAI API wrapper service."""
import os
from typing import Optional, AsyncIterator, Union, Literal
from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessageParam


class OpenAIService:
    """Wrapper around OpenAI API for chat completions."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI service.
        
        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)

    async def completion(
        self,
        config: dict
    ) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        """Generate a completion using OpenAI API.
        
        Args:
            config: Configuration dict with keys:
                - messages: List of ChatCompletionMessageParam
                - model: Model name (default: 'gpt-4o')
                - stream: Whether to stream response (default: False)
                - jsonMode: Whether to use JSON mode (default: False)
                - maxTokens: Max tokens in response (default: 8096)
        
        Returns:
            ChatCompletion or AsyncIterator of ChatCompletionChunk if streaming.
        
        Raises:
            ValueError: If API call fails.
        """
        messages = config.get('messages', [])
        model = config.get('model', 'gpt-4o')
        stream = config.get('stream', False)
        json_mode = config.get('jsonMode', False)
        max_tokens = config.get('maxTokens', 8096)

        try:
            # o1 models don't support certain parameters
            if model not in ['o1-mini', 'o1-preview']:
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=model,
                    stream=stream,
                    max_tokens=max_tokens,
                    response_format={
                        'type': 'json_object'
                    } if json_mode else {'type': 'text'}
                )
            else:
                # o1 models: no streaming, max_tokens, or response_format
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=model
                )

            return response

        except Exception as error:
            raise ValueError(f'Error in OpenAI completion: {error}')
