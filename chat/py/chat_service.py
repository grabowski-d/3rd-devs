"""Chat service with conversation memory and summarization."""

from typing import List, Optional
from openai.types.chat import ChatCompletionMessageParam

from .openai_service import OpenAIService


class ChatService:
    """Service for managing chat conversations with context."""

    def __init__(self, openai_service: OpenAIService):
        """Initialize chat service.

        Args:
            openai_service: OpenAI service instance.
        """
        self.openai_service = openai_service
        self.conversation_history: List[ChatCompletionMessageParam] = []
        self.summarization: str = ""

    async def get_response(
        self,
        user_message: str,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Get chat response with context.

        Args:
            user_message: User's message.
            model: Model to use.
            temperature: Temperature.
            system_prompt: System prompt to use.

        Returns:
            Assistant's response.
        """
        # Build messages list
        messages: List[ChatCompletionMessageParam] = []

        # Add system prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append(self._create_default_system_prompt())

        # Add conversation history
        messages.extend(self.conversation_history)

        # Add new user message
        messages.append({"role": "user", "content": user_message})

        # Get response
        response = await self.openai_service.async_completion(
            messages=messages,
            model=model,
            temperature=temperature,
        )

        assistant_message = response.choices[0].message.content or ""

        # Update conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append(
            {"role": "assistant", "content": assistant_message}
        )

        # Generate summarization
        self.summarization = await self._generate_summarization(
            user_message, assistant_message
        )

        return assistant_message

    async def _generate_summarization(
        self, user_message: str, assistant_message: str
    ) -> str:
        """Generate conversation summarization.

        Args:
            user_message: Last user message.
            assistant_message: Last assistant response.

        Returns:
            Updated summarization.
        """
        current_turn = f"User: {user_message}\nAssistant: {assistant_message}"

        summarization_prompt: ChatCompletionMessageParam = {
            "role": "system",
            "content": f"""Please summarize the following conversation turn in a concise manner.
            
Previous summary: {self.summarization or "No previous summary"}

Current turn:
{current_turn}

Provide an updated summary.""",
        }

        response = await self.openai_service.async_completion(
            messages=[summarization_prompt],
            model="gpt-4o",
            temperature=0.3,
        )

        return response.choices[0].message.content or ""

    def _create_default_system_prompt(self) -> ChatCompletionMessageParam:
        """Create default system prompt.

        Returns:
            System prompt message.
        """
        return {
            "role": "system",
            "content": f"""You are a helpful assistant who speaks using as few words as possible.

{f'Conversation context: {self.summarization}' if self.summarization else ''}

Let's chat!""",
        }

    def get_history(self) -> List[ChatCompletionMessageParam]:
        """Get conversation history.

        Returns:
            Conversation history.
        """
        return self.conversation_history.copy()

    def get_summarization(self) -> str:
        """Get current summarization.

        Returns:
            Conversation summarization.
        """
        return self.summarization

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []
        self.summarization = ""

    def set_summarization(self, summarization: str) -> None:
        """Set custom summarization.

        Args:
            summarization: New summarization.
        """
        self.summarization = summarization
