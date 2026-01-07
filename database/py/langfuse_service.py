"""Langfuse Service - Python implementation of database/LangfuseService.ts"""
import os
from typing import Dict, List, Optional, Any, Union
try:
    from langfuse import Langfuse
except ImportError:
    Langfuse = None


class LangfuseService:
    def __init__(self):
        if Langfuse is None:
            raise ImportError("langfuse package required")
        self.langfuse = Langfuse(
            secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
            public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
            base_url=os.getenv('LANGFUSE_HOST')
        )
    
    async def flush_async(self) -> None:
        self.langfuse.flush()
    
    def create_trace(self, options: Dict[str, str]) -> Any:
        return self.langfuse.trace(
            id=options['id'],
            name=options['name'],
            session_id=options['sessionId'],
            user_id=options['userId']
        )
    
    def create_span(self, trace: Any, name: str, input_data: Optional[Any] = None) -> Any:
        return trace.span(name=name, input=input_data)
    
    def finalize_span(self, span: Any, name: str, input_data: Any, output: Any) -> None:
        span.update(name=name, output=output)
        span.end()
    
    async def finalize_trace(self, trace: Any, input_data: Any, output: Any) -> None:
        trace.update(input=input_data, output=output)
        await self.flush_async()
    
    async def shutdown_async(self) -> None:
        self.langfuse.flush()
    
    def create_generation(self, trace: Any, name: str, input_data: Any, prompt: Optional[Any] = None, **config: Any) -> Any:
        return trace.generation(name=name, input=input_data, prompt=prompt, **config)
    
    def create_event(self, trace: Any, name: str, input_data: Optional[Any] = None, output: Optional[Any] = None) -> None:
        trace.event(name=name, input=str(input_data) if input_data else None, output=str(output) if output else None)
    
    def finalize_generation(self, generation: Any, output: Any, model: str, usage: Optional[Dict[str, Optional[int]]] = None) -> None:
        generation.update(output=output, model=model, usage=usage)
        generation.end()
    
    async def create_prompt(self, body: Dict[str, Any]) -> Any:
        return self.langfuse.create_prompt(**body)
    
    async def get_prompt(self, name: str, version: Optional[int] = None, options: Optional[Dict[str, Any]] = None) -> Any:
        if options is None:
            options = {}
        config = {k.replace('TtlSeconds', '_ttl_seconds').replace('MaxRetries', '_max_retries').replace('TimeoutMs', '_timeout_ms'): v for k, v in options.items()}
        return self.langfuse.get_prompt(name, version, **config)
    
    def compile_prompt(self, prompt: Any, variables: Optional[Dict[str, Any]] = None) -> Union[str, List[Dict[str, str]]]:
        compiled = prompt.compile(variables or {})
        if isinstance(compiled, str):
            return compiled
        elif isinstance(compiled, list):
            return [{'role': msg.get('role'), 'content': msg.get('content')} for msg in compiled]
        raise ValueError(f'Unexpected prompt result: {type(compiled)}')
    
    async def pre_fetch_prompts(self, prompt_names: List[str]) -> None:
        for name in prompt_names:
            await self.get_prompt(name)
