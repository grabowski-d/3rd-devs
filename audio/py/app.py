"""Example audio assistant application."""

import asyncio
from .openai_service import OpenAIService
from .assistant_service import AssistantService


async def main():
    """Run example audio assistant."""

    # Initialize services
    openai_service = OpenAIService()
    assistant = AssistantService(openai_service)

    print("\n" + "=" * 60)
    print("Audio Assistant Example")
    print("=" * 60 + "\n")

    # Example 1: Add memory
    print("1. Adding memory...")
    memory = await assistant.add_memory(
        title="User Preferences",
        content="User prefers Polish language responses and technical discussions",
        category="user",
    )
    print(f"   Added memory: {memory['id']}\n")

    # Example 2: Generate answer with context
    print("2. Generating answer with context...")
    try:
        messages = [
            {
                "role": "user",
                "content": "What is artificial intelligence?",
            },
        ]

        memories_context = await assistant.get_relevant_context(
            "artificial intelligence"
        )
        response = await assistant.answer(
            messages=messages,
            memories=memories_context or "No specific memories found",
        )

        answer = response.choices[0].message.content
        print(f"   Response: {answer[:200]}...\n")

        # Learn from response if applicable
        if assistant.should_learn(answer, "AI"):
            learning = await assistant.add_learning(
                topic="AI",
                content=answer[:500],
                source="assistant",
            )
            print(f"   Learned: {learning['id']}\n")

    except Exception as error:
        print(f"   Error: {error}\n")

    # Example 3: Transcription simulation
    print("3. Simulating transcription...")
    try:
        # In practice, would be real audio bytes
        test_transcription = "Hello, this is a test message"
        print(f"   Transcribed: {test_transcription}")
        print(f"   Token count: {openai_service.count_tokens(test_transcription)}\n")
    except Exception as error:
        print(f"   Error: {error}\n")

    # Example 4: Show learnings and memories
    print("4. Retrieving stored information...")
    memories = assistant.get_memories()
    learnings = assistant.get_learnings()
    print(f"   Stored memories: {len(memories)}")
    print(f"   Stored learnings: {len(learnings)}")

    if memories:
        print(f"   Latest memory: {memories[-1]['title']}")
    if learnings:
        print(f"   Latest learning: {learnings[-1]['topic']}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
