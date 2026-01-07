"""Example task categorization application."""

import asyncio
from .openai_service import OpenAIService
from .categorizer import TaskCategorizer


async def main():
    """Run example task categorization."""

    # Initialize services
    openai_service = OpenAIService()
    categorizer = TaskCategorizer(openai_service)

    print("\n" + "=" * 60)
    print("Task Categorization Example")
    print("=" * 60 + "\n")

    # Example tasks
    tasks = [
        "Prepare presentation for client meeting",
        "Buy groceries for dinner",
        "Read a novel",
        "Debug production issue",
        "Plan weekend trip",
    ]

    print("Tasks to categorize:")
    for i, task in enumerate(tasks, 1):
        print(f"  {i}. {task}")
    print()

    try:
        # Categorize tasks
        print("Categorizing tasks...\n")
        labels = await categorizer.categorize_batch(tasks)

        # Display results
        for task, label in zip(tasks, labels):
            print(f'Task: "{task}"')
            print(f'Label: {label}\n')

        # Statistics
        work_count = sum(1 for l in labels if l == "work")
        private_count = sum(1 for l in labels if l == "private")
        other_count = sum(1 for l in labels if l == "other")

        print("\nStatistics:")
        print(f"  Work tasks: {work_count}")
        print(f"  Private tasks: {private_count}")
        print(f"  Other tasks: {other_count}")

    except Exception as error:
        print(f"Error: {error}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
