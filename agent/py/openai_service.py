"""OpenAI service for agent."""
import os
from typing import List, Optional, Dict, Any
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam


class OpenAIService:
    """OpenAI API wrapper for agent system."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI service.
        
        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)

    async def completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = 'gpt-4o',
        json_mode: bool = False,
        max_tokens: int = 4096
    ) -> ChatCompletion:
        """Generate completion.
        
        Args:
            messages: Chat messages.
            model: Model name.
            json_mode: Whether to use JSON mode.
            max_tokens: Max tokens.
        
        Returns:
            ChatCompletion response.
        """
        try:
            kwargs: Dict[str, Any] = {
                'messages': messages,
                'model': model,
                'max_tokens': max_tokens,
            }
            
            if json_mode:
                kwargs['response_format'] = {'type': 'json_object'}
            
            return self.client.chat.completions.create(**kwargs)
        
        except Exception as error:
            raise ValueError(f'Error in OpenAI completion: {error}')
