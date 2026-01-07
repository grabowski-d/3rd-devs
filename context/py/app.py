"""Example document context application."""

import asyncio
from .openai_service import OpenAIService
from .context_service import ContextService


async def main():
    """Run example context management."""

    # Initialize services
    openai_service = OpenAIService()
    context_service = ContextService(openai_service)

    print("\n" + "=" * 60)
    print("Document Context Management Example")
    print("=" * 60 + "\n")

    # Add sample documents
    print("Adding documents...\n")

    doc1_content = \"\"\"Hybrid Search combines both lexical and semantic search:
    - Lexical search: Finds exact keyword matches
    - Semantic search: Understands meaning and context
    - Combined: Provides best results for information retrieval
    \"\"\"

    doc2_content = \"\"\"Vector embeddings are numerical representations of text:
    - Convert text to high-dimensional vectors
    - Similar texts have similar vectors
    - Used in semantic search and clustering
    \"\"\"

    uuid1 = context_service.add_document(
        content=doc1_content,
        title="Lesson 0302 — Wyszukiwanie hybrydowe",
    )
    uuid2 = context_service.add_document(
        content=doc2_content,
        title="Vector Embeddings Guide",
    )

    print(f"Added document 1: {uuid1}")
    print(f"Added document 2: {uuid2}\n")

    # List documents
    print("Available documents:")
    for doc in context_service.list_documents():
        print(f"  - {doc['title']} ({doc['uuid']})")
    print()

    # Query with context
    print("Processing query...\n")
    try:
        query = "Show me the list of available documents and explain hybrid search."
        response = await context_service.query(query)
        print(f"Query: {query}")
        print(f"Response:\n{response}\n")

    except Exception as error:
        print(f"Error: {error}\n")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
