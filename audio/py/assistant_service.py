"""Audio assistant service with learning and context management."""

import uuid
from typing import Any, Dict, List, Optional
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam

from .openai_service import OpenAIService


class AssistantService:
    """Service for managing audio assistant with learning capabilities."""

    def __init__(self, openai_service: OpenAIService):
        """Initialize assistant service.

        Args:
            openai_service: OpenAI service instance.
        """
        self.openai_service = openai_service
        self.memories: List[Dict[str, str]] = []
        self.learnings: List[Dict[str, str]] = []

    async def answer(
        self,
        messages: List[ChatCompletionMessageParam],
        model: str = "gpt-4o",
        stream: bool = False,
        json_mode: bool = False,
        max_tokens: int = 4096,
        memories: Optional[str] = None,
        knowledge: Optional[str] = None,
        learnings: Optional[str] = None,
    ) -> ChatCompletion:
        """Generate answer with context.

        Args:
            messages: Chat messages.
            model: Model to use.
            stream: Whether to stream.
            json_mode: Whether to use JSON mode.
            max_tokens: Max tokens.
            memories: Relevant memories context.
            knowledge: Knowledge base context.
            learnings: Learnings context.

        Returns:
            Chat completion response.
        """
        # Enrich messages with context
        enriched_messages = self._enrich_messages(
            messages, memories, knowledge, learnings
        )

        response = await self.openai_service.completion(
            messages=enriched_messages,
            model=model,
            stream=stream,
            json_mode=json_mode,
            max_tokens=max_tokens,
        )

        return response

    def _enrich_messages(
        self,
        messages: List[ChatCompletionMessageParam],
        memories: Optional[str] = None,
        knowledge: Optional[str] = None,
        learnings: Optional[str] = None,
    ) -> List[ChatCompletionMessageParam]:
        """Enrich messages with context.

        Args:
            messages: Original messages.
            memories: Memories to add.
            knowledge: Knowledge to add.
            learnings: Learnings to add.

        Returns:
            Enriched messages.
        """
        enriched = messages.copy()

        context_parts = []
        if memories:
            context_parts.append(f"Relevant memories:\n{memories}")
        if knowledge:
            context_parts.append(f"Knowledge base:\n{knowledge}")
        if learnings:
            context_parts.append(f"Previous learnings:\n{learnings}")

        if context_parts:
            context = "\n\n".join(context_parts)
            system_msg: ChatCompletionMessageParam = {
                "role": "system",
                "content": f"You have access to the following context:\n\n{context}",
            }
            enriched.insert(0, system_msg)

        return enriched

    async def get_relevant_context(self, query: str) -> str:
        """Get relevant context for query.

        Args:
            query: User query.

        Returns:
            Relevant context string.
        """
        # In production, would search memory system
        matching_memories = [
            m["content"] for m in self.memories if query.lower() in m.get("content", "").lower()
        ]
        return "\n".join(matching_memories) if matching_memories else ""

    def should_learn(self, response: str, topic: str) -> bool:
        """Determine if response should be learned.

        Args:
            response: Response text.
            topic: Topic being discussed.

        Returns:
            Whether to learn this response.
        """
        # Simple heuristic: learn if response is substantial
        return len(response) > 100

    async def add_learning(
        self,
        topic: str,
        content: str,
        source: Optional[str] = None,
    ) -> Dict[str, str]:
        """Add a learning.

        Args:
            topic: Topic of learning.
            content: Learning content.
            source: Source of learning.

        Returns:
            Learning record.
        """
        learning = {
            "id": str(uuid.uuid4()),
            "topic": topic,
            "content": content,
            "source": source or "user",
        }
        self.learnings.append(learning)
        return learning

    async def add_memory(
        self,
        title: str,
        content: str,
        category: Optional[str] = None,
    ) -> Dict[str, str]:
        """Add a memory.

        Args:
            title: Memory title.
            content: Memory content.
            category: Memory category.

        Returns:
            Memory record.
        """
        memory = {
            "id": str(uuid.uuid4()),
            "title": title,
            "content": content,
            "category": category or "general",
        }
        self.memories.append(memory)
        return memory

    def get_learnings(self, topic: Optional[str] = None) -> List[Dict[str, str]]:
        """Get learnings.

        Args:
            topic: Optional topic filter.

        Returns:
            List of learnings.
        """
        if topic:
            return [
                l for l in self.learnings
                if l.get("topic", "").lower() == topic.lower()
            ]
        return self.learnings

    def get_memories(self, category: Optional[str] = None) -> List[Dict[str, str]]:
        """Get memories.

        Args:
            category: Optional category filter.

        Returns:
            List of memories.
        """
        if category:
            return [
                m for m in self.memories
                if m.get("category", "").lower() == category.lower()
            ]
        return self.memories
