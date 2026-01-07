"""OpenAI Service with embedding and tokenization - Python implementation"""
import os
from typing import List, Dict, Any, Union
from openai import OpenAI
import tiktoken

class OpenAIService:
    def __init__(self):
        self.openai = OpenAI()
        self.tokenizers: Dict[str, Any] = {}
        self.IM_START = "<|im_start|>"
        self.IM_END = "<|im_end|>"
        self.IM_SEP = "<|im_sep|>"
        self.JINA_API_KEY = os.getenv('JINA_API_KEY')
    
    def _get_tokenizer(self, model_name: str):
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
            formatted_content += f"{self.IM_START}{message.get('role')}{self.IM_SEP}{message.get('content', '')}{self.IM_END}"
        formatted_content += f"{self.IM_START}assistant{self.IM_SEP}"
        tokens = tokenizer.encode(formatted_content)
        return len(tokens)
    
    async def create_embedding(self, text: str) -> List[float]:
        try:
            response = self.openai.embeddings.create(model="text-embedding-3-large", input=text)
            return response.data[0].embedding
        except Exception as error:
            print(f"Error creating embedding: {error}")
            raise
    
    async def create_jina_embedding(self, text: str) -> List[float]:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    'https://api.jina.ai/v1/embeddings',
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.JINA_API_KEY}'
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
                    raise Exception(f"HTTP error! status: {response.status_code}")
                data = response.json()
                return data['data'][0]['embedding']
        except Exception as error:
            print(f"Error creating Jina embedding: {error}")
            raise
    
    async def completion(self, messages: List[Dict[str, str]], model: str = "gpt-4o", stream: bool = False, json_mode: bool = False, max_tokens: int = 4096):
        try:
            chat_completion = self.openai.chat.completions.create(
                messages=messages,
                model=model,
                stream=stream,
                max_tokens=max_tokens,
                response_format={"type": "json_object"} if json_mode else {"type": "text"}
            )
            return chat_completion if stream else self._format_response(chat_completion)
        except Exception as error:
            print(f"Error in OpenAI completion: {error}")
            raise
    
    def _format_response(self, response: Any) -> Dict[str, Any]:
        return {
            'id': response.id,
            'model': response.model,
            'created': response.created,
            'choices': [{'message': {'role': c.message.role, 'content': c.message.content}, 'finish_reason': c.finish_reason} for c in response.choices],
            'usage': {'prompt_tokens': response.usage.prompt_tokens, 'completion_tokens': response.usage.completion_tokens, 'total_tokens': response.usage.total_tokens}
        }
    
    async def calculate_image_tokens(self, width: int, height: int, detail: str = 'high') -> int:
        token_cost = 0
        if detail == 'low':
            return 85
        
        MAX_DIMENSION = 2048
        SCALE_SIZE = 768
        
        if width > MAX_DIMENSION or height > MAX_DIMENSION:
            aspect_ratio = width / height
            if aspect_ratio > 1:
                width = MAX_DIMENSION
                height = int(MAX_DIMENSION / aspect_ratio)
            else:
                height = MAX_DIMENSION
                width = int(MAX_DIMENSION * aspect_ratio)
        
        if width >= height and height > SCALE_SIZE:
            width = int((SCALE_SIZE / height) * width)
            height = SCALE_SIZE
        elif height > width and width > SCALE_SIZE:
            height = int((SCALE_SIZE / width) * height)
            width = SCALE_SIZE
        
        num_squares = ((width + 511) // 512) * ((height + 511) // 512)
        token_cost = (num_squares * 170) + 85
        return token_cost
