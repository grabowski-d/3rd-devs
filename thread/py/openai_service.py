"""OpenAI Service - Python implementation of thread/OpenAIService.ts"""
from typing import List, Dict, Union, Any
from openai import OpenAI

class OpenAIService:
    def __init__(self):
        self.openai = OpenAI()
    
    async def completion(self, messages: List[Dict[str, str]], model: str = "gpt-4", stream: bool = False) -> Union[Dict[str, Any], Any]:
        try:
            chat_completion = self.openai.chat.completions.create(messages=messages, model=model, stream=stream)
            return chat_completion if stream else self._format_response(chat_completion)
        except Exception as error:
            print(f"Error in OpenAI completion: {error}")
            raise
    
    def _format_response(self, response: Any) -> Dict[str, Any]:
        return {
            'id': response.id, 'model': response.model, 'created': response.created,
            'choices': [{'message': {'role': c.message.role, 'content': c.message.content}, 'finish_reason': c.finish_reason} for c in response.choices],
            'usage': {'prompt_tokens': response.usage.prompt_tokens, 'completion_tokens': response.usage.completion_tokens, 'total_tokens': response.usage.total_tokens}
        }
