"""Example application using Algolia search service."""

import asyncio
import uuid
from typing import Any, Dict

from .service import AlgoliaService


async def main():
    """Run example Algolia application."""

    # Initialize service
    algolia_service = AlgoliaService()

    # Sample data
    data = [
        {
            "author": "Adam",
            "text": "I believe in writing clean, maintainable code. Refactoring should be a regular part of our development process.",
        },
        {
            "author": "Kuba",
            "text": "Test-driven development has significantly improved the quality of our codebase. Let's make it a standard practice.",
        },
        {
            "author": "Mateusz",
            "text": "Optimizing our CI/CD pipeline could greatly enhance our deployment efficiency. We should prioritize this in our next sprint.",
        },
    ]

    index_name = "dev_comments"

    print("\n" + "=" * 60)
    print("Algolia Search Example")
    print("=" * 60 + "\n")

    # Check if index exists
    print("Checking if index exists...")
    try:
        indices = await algolia_service.list_indices()
        index_exists = any(
            idx.get("name") == index_name
            for idx in indices.get("items", [])
        )

        if not index_exists:
            print(f"\nAdding data to '{index_name}' index...")
            for item in data:
                object_id = str(uuid.uuid4())
                await algolia_service.add_or_update_object(
                    index_name,
                    object_id,
                    {**item, "objectID": object_id},
                )
            print(f"✓ Added {len(data)} items")
        else:
            print(f"✓ Index '{index_name}' already exists")

        # Perform sample search
        print("\nSearching for 'code'...")
        search_result = await algolia_service.search_single_index(
            index_name,
            "code",
            {"queryParameters": {"filters": "author:Adam"}},
        )

        hits = search_result.get("hits", [])
        print(f"\nFound {len(hits)} results:\n")

        for i, hit in enumerate(hits, 1):
            author = hit.get("author", "Unknown")
            text = hit.get("text", "")
            text_preview = text[:45] + ("..." if len(text) > 45 else "")
            object_id = hit.get("objectID", "")

            print(f"{i}. Author: {author}")
            print(f"   Text: {text_preview}")
            print(f"   ObjectID: {object_id}")
            print()

    except Exception as error:
        print(f"Error: {error}")
        print("\nMake sure:")
        print("1. ALGOLIA_APP_ID environment variable is set")
        print("2. ALGOLIA_API_KEY environment variable is set")
        print("3. algoliasearch package is installed: pip install algoliasearch")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
