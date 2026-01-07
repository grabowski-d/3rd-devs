"""Example application using Algolia service.

Demonstrates:
- Creating/checking indices
- Adding data to indices
- Searching with filters
- Result formatting
"""

import asyncio
import uuid
import os
from algolia_service import AlgoliaService


async def main() -> None:
    """Main application function."""
    # Initialize Algolia service
    app_id = os.getenv("ALGOLIA_APP_ID", "")
    api_key = os.getenv("ALGOLIA_API_KEY", "")
    
    if not app_id or not api_key:
        print("Error: ALGOLIA_APP_ID and ALGOLIA_API_KEY environment variables are required")
        return

    algolia_service = AlgoliaService(app_id, api_key)

    # Sample data
    data = [
        {
            "author": "Adam",
            "text": "I believe in writing clean, maintainable code. Refactoring should be a regular part of our development process."
        },
        {
            "author": "Kuba",
            "text": "Test-driven development has significantly improved the quality of our codebase. Let's make it a standard practice."
        },
        {
            "author": "Mateusz",
            "text": "Optimizing our CI/CD pipeline could greatly enhance our deployment efficiency. We should prioritize this in our next sprint."
        },
    ]

    index_name = "dev_comments"

    # Check if index exists
    print(f"Checking if index '{index_name}' exists...")
    indices_response = await algolia_service.list_indices()
    indices = indices_response.get("items", [])
    index_exists = any(index["name"] == index_name for index in indices)

    if not index_exists:
        # Add data only if index doesn't exist
        print(f"Index does not exist. Adding {len(data)} documents...")
        for item in data:
            object_id = str(uuid.uuid4())
            await algolia_service.add_or_update_object(
                index_name, object_id, {**item, "objectID": object_id}
            )
        print("Data added to index")
    else:
        print("Index already exists. Skipping data addition.")

    # Perform a sample search
    print("\nPerforming search...")
    query = "code"
    search_result = await algolia_service.search_single_index(
        index_name,
        query,
        options={
            "query_parameters": {
                "filters": "author:Adam"
            }
        },
    )

    # Format and display results
    print(f"\nSearch results for '{query}' (filtered by author:Adam):")
    print(f"Total hits: {search_result.nbHits}")
    print(f"Processing time: {search_result.processingTimeMS}ms\n")

    formatted_results = [
        {
            "Author": hit.get("author", "N/A"),
            "Text": hit.get("text", "")[:45] + ("..." if len(hit.get("text", "")) > 45 else ""),
            "ObjectID": hit.get("objectID", "N/A"),
        }
        for hit in search_result.hits
    ]

    if formatted_results:
        print("Results:")
        for result in formatted_results:
            print(f"  - {result}")
    else:
        print("No results found.")


if __name__ == "__main__":
    asyncio.run(main())
