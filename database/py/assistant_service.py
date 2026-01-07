"""Assistant Service - Python implementation of database/AssistantService.ts"""
import uuid
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from .database_service import DatabaseService
from .openai_service import OpenAIService
from .langfuse_service import LangfuseService


@dataclass
class ParsingError:
    error: str
    result: bool


@dataclass
class ShouldLearnResponse:
    _thinking: str
    add: Optional[List[str]] = None
    update: Optional[List[Dict[str, str]]] = None


class AssistantService:
    def __init__(
        self,
        database_service: DatabaseService,
        openai_service: OpenAIService,
        langfuse_service: LangfuseService
    ):
        self.database_service = database_service
        self.openai_service = openai_service
        self.langfuse_service = langfuse_service

    async def answer(
        self,
        config: Dict[str, Any],
        trace: Any
    ) -> Dict[str, Any]:
        """
        Process a chat message and save it along with the response.
        
        Args:
            config: Configuration dict with keys:
                - conversation_id: str
                - messages: List[Dict] with role and content
                - model: Optional[str]
                - stream: Optional[bool]
                - jsonMode: Optional[bool]
                - maxTokens: Optional[int]
            trace: Langfuse trace object
            
        Returns:
            OpenAI completion response
        """
        messages = config.get('messages', [])
        conversation_id = config.get('conversation_id')
        
        # Extract user message
        user_message = 'No content'
        if messages and len(messages) > 0:
            last_message = messages[-1]
            user_message = last_message.get('content', 'No content')
        
        # Save user message to database
        await self.database_service.insert_message({
            'uuid': str(uuid.uuid4()),
            'conversation_id': conversation_id,
            'content': user_message,
            'role': 'user'
        })
        
        # Get prompt from Langfuse
        prompt = await self.langfuse_service.get_prompt('Answer', 1)
        system_message = prompt.compile()[0]
        
        # Prepare thread with system message
        thread = [system_message]
        thread.extend([msg for msg in messages if msg.get('role') != 'system'])
        
        # Create generation for tracing
        rest_config = {k: v for k, v in config.items() if k not in ['messages', 'conversation_id']}
        generation = self.langfuse_service.create_generation(
            trace, "Answer", thread, prompt, **rest_config
        )
        
        try:
            # Get completion from OpenAI
            completion = await self.openai_service.completion({
                **rest_config,
                'messages': thread
            })
            
            answer = completion.get('choices', [{}])[0].get('message', {}).get('content', 'No response')
            
            # Save assistant response to database
            await self.database_service.insert_message({
                'uuid': str(uuid.uuid4()),
                'conversation_id': conversation_id,
                'content': answer,
                'role': 'assistant'
            })
            
            # Finalize generation tracing
            usage = completion.get('usage', {})
            self.langfuse_service.finalize_generation(
                generation,
                completion.get('choices', [{}])[0].get('message'),
                completion.get('model', 'unknown'),
                {
                    'promptTokens': usage.get('prompt_tokens'),
                    'completionTokens': usage.get('completion_tokens'),
                    'totalTokens': usage.get('total_tokens')
                }
            )
            
            return completion
            
        except Exception as error:
            error_msg = str(error) if isinstance(error, Exception) else str(error)
            self.langfuse_service.finalize_generation(
                generation,
                {'error': error_msg},
                'unknown'
            )
            raise
