"""Task categorizer service for label assignment."""

from typing import List, Literal, Optional
from openai.types.chat import ChatCompletionMessageParam

from .openai_service import OpenAIService

TaskCategory = Literal["work", "private", "other"]


class TaskCategorizer:
    """Service for categorizing tasks into labels."""

    def __init__(self, openai_service: OpenAIService):
        """Initialize task categorizer.

        Args:
            openai_service: OpenAI service instance.
        """
        self.openai_service = openai_service

    async def add_label(self, task: str) -> TaskCategory:
        """Categorize a task and assign a label.

        Args:
            task: Task description.

        Returns:
            Task category: 'work', 'private', or 'other'.
        """
        messages: List[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": (
                    "You are a task categorizer. Categorize the given task "
                    "as 'work', 'private', or 'other'. "
                    "Respond with only the category name."
                ),
            },
            {"role": "user", "content": task},
        ]

        try:
            completion = await self.openai_service.completion(
                messages=messages,
                model="gpt-4o-mini",
                max_tokens=1,
                temperature=0,
            )

            content = completion.choices[0].message.content
            if content:
                label = content.strip().lower()
                if label in ["work", "private"]:
                    return label  # type: ignore
                return "other"
            return "other"

        except Exception as error:
            print(f"Error in categorization: {error}")
            return "other"

    async def categorize_batch(self, tasks: List[str]) -> List[TaskCategory]:
        """Categorize multiple tasks.

        Args:
            tasks: List of task descriptions.

        Returns:
            List of categories.
        """
        import asyncio

        results = await asyncio.gather(
            *[self.add_label(task) for task in tasks]
        )
        return results  # type: ignore

    def get_valid_categories(self) -> List[str]:
        """Get list of valid categories.

        Returns:
            Valid category names.
        """
        return ["work", "private", "other"]
