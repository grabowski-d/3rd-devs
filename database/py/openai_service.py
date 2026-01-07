"""OpenAI Service - Python implementation of database/OpenAIService.ts"""
import json
from typing import Dict, List, Optional, Any, Union
from openai import OpenAI
import tiktoken

class ParsingError:
    def __init__(self, error: str, result: bool = False):
        self.error = error
        self.result = result

class OpenAIService:
    IM_START = "<|im_start|>"
    IM_END = "<|im_end|>"
    IM_SEP = "<|im_sep|>"
    
    def __init__(self):
        self.client = OpenAI()
        self.tokenizers: Dict[str, Any] = {}
    
    def _get_tokenizer(self, model_name: str) -> Any:
        if model_name not in self.tokenizers:
            try:
                self.tokenizers[model_name] = tiktoken.encoding_for_model(model_name)
            except KeyError:
                self.tokenizers[model_name] = tiktoken.get_encoding("cl100k_base")
        return self.tokenizers[model_name]
    
    async def count_tokens(self, messages: List[Dict[str, str]], model: str = 'gpt-4o') -> int:
        tokenizer = self._get_tokenizer(model)
        formatted_content = ''
        for message in messages:
            role = message.get('role', '')
            content = message.get('content', '')
            formatted_content += f"{self.IM_START}{role}{self.IM_SEP}{content}{self.IM_END}"
        formatted_content += f"{self.IM_START}assistant{self.IM_SEP}"
        tokens = tokenizer.encode(formatted_content)
        return len(tokens)
    
    async def completion(self, config: Dict[str, Any]) -> Union[Dict[str, Any], Any]:
        messages = config.get('messages', [])
        model = config.get('model', 'gpt-4o')
        stream = config.get('stream', False)
        temperature = config.get('temperature', 0)
        json_mode = config.get('jsonMode', False)
        max_tokens = config.get('maxTokens', 4096)
        
        try:
            response_format = {"type": "json_object"} if json_mode else {"type": "text"}
            completion = self.client.chat.completions.create(
                messages=messages, model=model, stream=stream, temperature=temperature,
                max_tokens=max_tokens, response_format=response_format
            )
            return completion if stream else self._format_response(completion)
        except Exception as error:
            print(f"Error in OpenAI completion: {error}")
            raise
    
    def _format_response(self, response: Any) -> Dict[str, Any]:
        return {
            'id': response.id, 'model': response.model, 'created': response.created,
            'choices': [{'message': {'role': c.message.role, 'content': c.message.content}, 'finish_reason': c.finish_reason, 'index': c.index} for c in response.choices],
            'usage': {'prompt_tokens': response.usage.prompt_tokens, 'completion_tokens': response.usage.completion_tokens, 'total_tokens': response.usage.total_tokens}
        }
    
    def is_stream_response(self, response: Any) -> bool:
        return hasattr(response, '__aiter__')
    
    def parse_json_response(self, response: Dict[str, Any]) -> Union[Dict[str, Any], ParsingError]:
        try:
            content = response.get('choices', [{}])[0].get('message', {}).get('content')
            if not content:
                raise ValueError('Invalid response structure')
            return json.loads(content)
        except Exception as error:
            print(f'Error parsing JSON response: {error}')
            return ParsingError('Failed to process response', False)
    
    async def create_embedding(self, text: str) -> List[float]:
        try:
            response = self.client.embeddings.create(model="text-embedding-3-large", input=text)
            return response.data[0].embedding
        except Exception as error:
            print(f"Error creating embedding: {error}")
            raise
