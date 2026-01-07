"""OpenAI service for better RAG."""
import os
from typing import List, Union, Optional
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
import tiktoken

class OpenAIService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)
        self.tokenizers = {}
    
    def _get_tokenizer(self, model_name: str):
        if model_name not in self.tokenizers:
            try:
                self.tokenizers[model_name] = tiktoken.encoding_for_model(model_name)
            except KeyError:
                self.tokenizers[model_name] = tiktoken.get_encoding('cl100k_base')
        return self.tokenizers[model_name]
    
    async def create_embedding(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model='text-embedding-3-large',
            input=text,
        )
        return response.data[0].embedding
    
    async def completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = 'gpt-4o',
        json_mode: bool = False,
        max_tokens: int = 4096
    ) -> ChatCompletion:
        return self.client.chat.completions.create(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            response_format={'type': 'json_object'} if json_mode else {'type': 'text'}
        )
