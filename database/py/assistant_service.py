"""Assistant service for handling conversations."""
from typing import Dict, Any, List, Optional
import uuid
from dataclasses import dataclass
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
from .database_service import DatabaseService
from .openai_service import OpenAIService
from .langfuse_service import LangfuseService, LangfuseTraceClient


@dataclass
class ShouldLearnResponse:
    """Response for learning decision."""
    thinking: str
    add: List[str] = None
    update: List[Dict[str, str]] = None


@dataclass
class ParsingError:
    """Error response structure."""
    error: str
    result: bool = False


class AssistantService:
    """Service for handling assistant conversations."""

    def __init__(
        self,
        database_service: DatabaseService,
        openai_service: OpenAIService,
        langfuse_service: LangfuseService
    ):
        """Initialize assistant service.
        
        Args:
            database_service: Database service instance.
            openai_service: OpenAI service instance.
            langfuse_service: Langfuse service instance.
        """
        self.database_service = database_service
        self.openai_service = openai_service
        self.langfuse_service = langfuse_service

    async def answer(
        self,
        config: Dict[str, Any],
        trace: LangfuseTraceClient
    ) -> ChatCompletion:
        """Generate an answer to user message.
        
        Args:
            config: Configuration dict with:
                - conversation_id: Conversation ID
                - messages: List of chat messages
                - model: Optional model name
                - stream: Optional stream flag
                - jsonMode: Optional JSON mode flag
                - maxTokens: Optional max tokens
            trace: Langfuse trace client for observability.
        
        Returns:
            ChatCompletion response.
        """
        messages = config.get('messages', [])
        conversation_id = config.get('conversation_id')

        # Get last user message
        user_message = ''
        if messages:
            last_msg = messages[-1]
            user_message = last_msg.get('content', '') if isinstance(last_msg, dict) else ''

        # Insert user message to database
        await self.database_service.insert_message({
            'uuid': str(uuid.uuid4()),
            'conversation_id': conversation_id,
            'content': user_message,
            'role': 'user'
        })

        # Get system prompt from Langfuse
        try:
            prompt = await self.langfuse_service.get_prompt('Answer', 1)
            system_message = prompt.compile()
        except Exception:
            system_message = 'You are a helpful assistant.'

        # Build message thread
        thread: List[ChatCompletionMessageParam] = []
        if isinstance(system_message, str):
            thread.append({'role': 'system', 'content': system_message})
        elif isinstance(system_message, list):
            thread.extend(system_message)

        # Add non-system messages from input
        for msg in messages:
            if msg.get('role') != 'system':
                thread.append(msg)

        # Create generation tracking
        generation = self.langfuse_service.create_generation(
            trace,
            'Answer',
            thread,
            None,
            {k: v for k, v in config.items() if k not in ['messages', 'conversation_id']}
        )

        try:
            # Get completion from OpenAI
            completion = await self.openai_service.completion({
                **config,
                'messages': thread
            })

            if not isinstance(completion, ChatCompletion):
                raise ValueError('Expected ChatCompletion, got streaming response')

            # Extract answer
            answer = completion.choices[0].message.content or 'No response'

            # Store assistant message
            await self.database_service.insert_message({
                'uuid': str(uuid.uuid4()),
                'conversation_id': conversation_id,
                'content': answer,
                'role': 'assistant'
            })

            # Finalize generation in Langfuse
            self.langfuse_service.finalize_generation(
                generation,
                completion.choices[0].message,
                completion.model,
                {
                    'promptTokens': completion.usage.prompt_tokens if completion.usage else 0,
                    'completionTokens': completion.usage.completion_tokens if completion.usage else 0,
                    'totalTokens': completion.usage.total_tokens if completion.usage else 0,
                }
            )

            return completion

        except Exception as error:
            # Track error in generation
            self.langfuse_service.finalize_generation(
                generation,
                {'error': str(error)},
                'unknown'
            )
            raise
