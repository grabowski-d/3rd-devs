"""Example memory application."""

import asyncio
import uuid
from audio_map.py.openai_service import OpenAIService
from audio_map.py.langfuse_service import LangfuseService
from .memory_service import MemoryService


async def main():
    """Run example memory operations."""

    # Initialize services
    openai_service = OpenAIService()
    langfuse_service = LangfuseService()
    memory_service = MemoryService(
        openai_service, 
        langfuse_service,
        base_dir="memory/py/memories_data"
    )

    await memory_service.initialize()

    trace = langfuse_service.create_trace(
        id=str(uuid.uuid4()),
        name="MemoryExample",
        session_id=str(uuid.uuid4())
    )

    print("\n" + "=" * 60)
    print("Memory Service Example")
    print("=" * 60 + "\n")

    try:
        # Create a memory
        print("Creating memory...")
        memory_data = {
            "category": "profiles",
            "subcategory": "basic",
            "name": "User Profile",
            "content": {
                "text": "The user is a software engineer interested in AI and Python."
            },
            "metadata": {
                "tags": ["profile", "work", "python"],
                "confidence": 1.0
            }
        }
        
        created = await memory_service.create_memory(memory_data, trace)
        print(f"Created: {created['uuid']} - {created['name']}")

        # Search similar
        print("\nSearching similar memories...")
        query = "What does the user do?"
        results = await memory_service.search_similar_memories(query)
        
        for res in results:
            print(f"  - {res['name']} ({res['similarity']:.3f}): {res['content']['text']}")

        # Recall
        print("\nRecalling memories...")
        recall_xml = await memory_service.recall([query], trace)
        print("Recall Result:")
        print(recall_xml)

    except Exception as error:
        print(f"Error: {error}")

    finally:
        langfuse_service.shutdown()

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
