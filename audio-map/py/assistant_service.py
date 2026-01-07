"""Assistant service for audio map application."""

from typing import Dict, List, Optional
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam

from .openai_service import OpenAIService
from .langfuse_service import LangfuseService


class AssistantService:
    """Service for managing assistant interactions."""

    def __init__(
        self, openai_service: OpenAIService, langfuse_service: LangfuseService
    ):
        """Initialize assistant service.

        Args:
            openai_service: OpenAI service instance.
            langfuse_service: Langfuse service instance.
        """
        self.openai_service = openai_service
        self.langfuse_service = langfuse_service

    async def answer(
        self,
        config: Dict[str, Any],
        trace: Any,
    ) -> ChatCompletion:
        """Generate answer with tracing.

        Args:
            config: Configuration dictionary including messages and model parameters.
            trace: Langfuse trace object.

        Returns:
            Chat completion response.
        """
        messages = config.pop("messages", [])
        
        # Extract other config parameters
        model = config.get("model", "gpt-4o")
        stream = config.get("stream", False)
        json_mode = config.get("jsonMode", False)
        max_tokens = config.get("maxTokens", 4096)
        
        # Remove custom fields if they exist in config but aren't used by OpenAI directly
        # or use them if implemented. For now, we pass standard params.
        
        generation = self.langfuse_service.create_generation(
            trace=trace,
            name="Answer",
            input=messages,
            model=model,
        )

        try:
            response = await self.openai_service.completion(
                messages=messages,
                model=model,
                stream=stream,
                json_mode=json_mode,
                max_tokens=max_tokens,
            )

            # Calculate usage if available
            usage = None
            if hasattr(response, "usage") and response.usage:
                usage = {
                    "promptTokens": response.usage.prompt_tokens,
                    "completionTokens": response.usage.completion_tokens,
                    "totalTokens": response.usage.total_tokens,
                }

            self.langfuse_service.finalize_generation(
                generation=generation,
                output=response.choices[0].message if not stream else "Streamed response",
                model=model,
                usage=usage,
            )
            return response

        except Exception as error:
            self.langfuse_service.finalize_generation(
                generation=generation,
                output={"error": str(error)},
                model=model,
            )
            raise error

    async def get_relevant_context(self, query: str) -> str:
        """Get relevant context for query.

        Args:
            query: User query.

        Returns:
            Relevant context string.
        """
        # Note: In the TS file, this method referenced 'this.memoryService' 
        # which was not defined in the class. Assuming implementation needed or placeholder.
        # For now, returning empty string or needs memory service injection.
        return ""
