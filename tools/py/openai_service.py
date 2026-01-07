"""OpenAI service with function calling support."""
import os
from typing import List, Union, Optional, Any, Dict
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam, ChatCompletionToolParam


class OpenAIService:
    """OpenAI API wrapper with tool/function calling support."""

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
        tools: Optional[List[ChatCompletionToolParam]] = None,
        tool_choice: Optional[str] = None,
        json_mode: bool = False,
        max_tokens: int = 4096
    ) -> ChatCompletion:
        """Generate completion with optional function calling.
        
        Args:
            messages: Chat messages.
            model: Model name.
            tools: List of available tools/functions.
            tool_choice: Tool choice strategy ('auto', 'required', or tool name).
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
            
            if tools:
                kwargs['tools'] = tools
                if tool_choice:
                    kwargs['tool_choice'] = tool_choice
            
            completion = self.client.chat.completions.create(**kwargs)
            return completion
        
        except Exception as error:
            raise ValueError(f'Error in OpenAI completion: {error}')

    async def extract_tool_calls(self, response: ChatCompletion) -> List[Dict[str, Any]]:
        """Extract tool calls from response.
        
        Args:
            response: ChatCompletion response.
        
        Returns:
            List of tool calls with id, name, and arguments.
        """
        tool_calls = []
        
        for choice in response.choices:
            if choice.message.tool_calls:
                for tool_call in choice.message.tool_calls:
                    tool_calls.append({
                        'id': tool_call.id,
                        'name': tool_call.function.name,
                        'arguments': tool_call.function.arguments
                    })
        
        return tool_calls
