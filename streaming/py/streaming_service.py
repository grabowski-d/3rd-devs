"""Service for streaming chat completions."""
import json
import uuid
from typing import List, AsyncIterator, Dict, Any, Optional
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionChunk
from .openai_service import OpenAIService


class StreamingService:
    """Service for managing streaming chat completions."""

    def __init__(self, openai_service: OpenAIService):
        """Initialize streaming service.
        
        Args:
            openai_service: OpenAI service instance.
        """
        self.openai_service = openai_service

    async def completion(
        self,
        messages: List[ChatCompletionMessageParam],
        stream: bool = False
    ) -> AsyncIterator[str]:
        """Generate chat completion with SSE formatting.
        
        Args:
            messages: List of chat messages.
            stream: Whether to stream response.
        
        Yields:
            SSE formatted chunks.
        """
        conversation_uuid = str(uuid.uuid4())

        system_prompt: ChatCompletionMessageParam = {
            'role': 'system',
            'content': 'You are a helpful assistant who speaks using as fewest words as possible.'
        }

        try:
            if stream:
                # Create example starting chunk
                starting_chunk: ChatCompletionChunk = {
                    'id': f'chatcmpl-{int(__import__("time").time() * 1000)}',
                    'object': 'chat.completion.chunk',
                    'created': int(__import__("time").time()),
                    'model': 'gpt-4',
                    'system_fingerprint': f'fp_{uuid.uuid4().hex[:15]}',
                    'choices': [{
                        'index': 0,
                        'delta': {'role': 'assistant', 'content': 'starting response'},
                        'logprobs': None,
                        'finish_reason': None
                    }]
                }

                yield f'data: {json.dumps(starting_chunk)}\n\n'

                # Get streaming response
                result = await self.openai_service.completion(
                    [system_prompt, *messages],
                    'gpt-4',
                    stream=True
                )

                async for chunk in result:
                    yield f'data: {json.dumps(chunk.model_dump())}\n\n'

                # Send done signal
                yield 'data: [DONE]\n\n'

            else:
                # Non-streaming response
                result = await self.openai_service.completion(
                    [system_prompt, *messages],
                    'gpt-4',
                    stream=False
                )
                yield json.dumps({
                    **result.model_dump(),
                    'conversationUUID': conversation_uuid
                })

        except Exception as error:
            error_chunk: Dict[str, Any] = {
                'id': f'chatcmpl-{int(__import__("time").time() * 1000)}',
                'object': 'chat.completion.chunk',
                'created': int(__import__("time").time()),
                'model': 'gpt-4',
                'system_fingerprint': f'fp_{uuid.uuid4().hex[:15]}',
                'choices': [{
                    'index': 0,
                    'delta': {'content': f'An error occurred during streaming: {error}'},
                    'logprobs': None,
                    'finish_reason': 'stop'
                }]
            }
            yield f'data: {json.dumps(error_chunk)}\n\n'
            yield 'data: [DONE]\n\n'
