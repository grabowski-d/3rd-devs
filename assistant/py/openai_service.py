"""OpenAI integration for assistant module."""

import logging
from typing import Any, AsyncIterator, Dict, List, Literal, Optional, Union

try:
    import openai
    from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessageParam
except ImportError:
    openai = None
    ChatCompletion = None
    ChatCompletionChunk = None
    ChatCompletionMessageParam = None

logger = logging.getLogger(__name__)


class OpenAIService:
    """OpenAI API wrapper for chat completions."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize OpenAI service.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        if not openai:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )
        
        if api_key:
            openai.api_key = api_key
        
        self.client = openai.OpenAI()
        logger.info("Initialized OpenAI service")

    async def completion(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = "gpt-4o",
        stream: bool = False,
        json_mode: bool = False,
        max_tokens: int = 8096,
    ) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        """Get completion from OpenAI.

        Args:
            messages: List of message dicts with role and content
            model: Model to use (default: gpt-4o)
            stream: Whether to stream the response
            json_mode: Whether to use JSON mode
            max_tokens: Maximum tokens in response

        Returns:
            ChatCompletion or async iterator of chunks if streaming
        """
        try:
            # o1 models don't support streaming, json_mode, or max_tokens
            is_o1_model = model in ("o1-mini", "o1-preview")
            
            if is_o1_model:
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=model,
                )
            else:
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=model,
                    stream=stream,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"} if json_mode else {"type": "text"},
                )
            
            logger.debug(f"Completion request sent to {model}")
            return response
        except Exception as e:
            logger.error(f"Error in OpenAI completion: {e}")
            raise

    def completion_sync(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = "gpt-4o",
        stream: bool = False,
        json_mode: bool = False,
        max_tokens: int = 8096,
    ) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:
        """Synchronous wrapper for completion.

        Args:
            messages: List of message dicts with role and content
            model: Model to use (default: gpt-4o)
            stream: Whether to stream the response
            json_mode: Whether to use JSON mode
            max_tokens: Maximum tokens in response

        Returns:
            ChatCompletion or iterator of chunks if streaming
        """
        return self.completion(
            messages=messages,
            model=model,
            stream=stream,
            json_mode=json_mode,
            max_tokens=max_tokens,
        )
