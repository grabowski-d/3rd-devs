"""Example chat application with conversation management."""

import asyncio
from .openai_service import OpenAIService
from .chat_service import ChatService


async def main():
    """Run example chat application."""

    # Initialize services
    openai_service = OpenAIService()
    chat_service = ChatService(openai_service)

    print("\n" + "=" * 60)
    print("Chat Service Example")
    print("=" * 60 + "\n")

    # Demo conversation
    demo_messages = [
        "Hi! I'm Adam",
        "How are you?",
        "Do you know my name?",
    ]

    for user_message in demo_messages:
        print(f"Adam: {user_message}")

        try:
            response = await chat_service.get_response(
                user_message=user_message,
                system_prompt="You are Alice, a helpful assistant who speaks using as few words as possible.",
            )
            print(f"Alice: {response}\n")

        except Exception as error:
            print(f"Error: {error}\n")

    # Show conversation summary
    print("\nConversation Summary:")
    print("-" * 60)
    print(chat_service.get_summarization())
    print("-" * 60)

    # Show history
    print(f"\nTotal messages: {len(chat_service.get_history())}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
