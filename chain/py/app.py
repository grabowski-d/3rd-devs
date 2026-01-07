"""Example chain-of-thought QA application."""

import asyncio
from .openai_service import OpenAIService
from .chain_of_thought import ChainOfThought


async def main():
    """Run example chain-of-thought QA."""

    # Initialize services
    openai_service = OpenAIService()
    chain = ChainOfThought(openai_service)

    print("\n" + "=" * 60)
    print("Chain-of-Thought QA Example")
    print("=" * 60 + "\n")

    # Display available people
    print("Available people:")
    for person in chain.get_all_people():
        print(
            f"  {person['name']} (ID: {person['id']}) - "
            f"{person['age']} years old, {person['occupation']}"
        )
    print()

    # Example questions
    questions = [
        "Who is the oldest person?",
        "Tell me about Adam's hobby",
        "What does Michał do for a living?",
        "How old is Jakub?",
        "Who likes photography?",
    ]

    print("Processing questions...\n")

    for question in questions:
        try:
            result = await chain.process_question(question)
            print(f"Question: {result['question']}")
            print(f"Routed to: {result['person_name']}")
            print(f"Answer: {result['answer']}")
            print("-" * 60)

        except Exception as error:
            print(f"Error processing question: {error}")
            print("-" * 60)

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
