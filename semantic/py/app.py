"""Semantic search example."""

import asyncio
from .openai_service import OpenAIService
from .text_service import TextService


async def main():
    openai_service = OpenAIService()
    text_service = TextService()

    print("\n" + "="*60)
    print("Semantic Search Example")
    print("="*60 + "\n")

    try:
        text = "Python is a great programming language for AI and machine learning."
        embedding = await openai_service.create_embedding(text)
        print(f"Created embedding for: {text[:50]}...")
        print(f"Embedding dimension: {len(embedding)}\n")

    except Exception as e:
        print(f"Error: {e}")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
