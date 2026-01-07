"""Keyword extraction example."""

import asyncio
from .keyword_extractor import KeywordExtractor


async def main():
    print("\n" + "="*60)
    print("Keyword Extraction Example")
    print("="*60 + "\n")

    extractor = KeywordExtractor()
    text = "Python programming machine learning artificial intelligence"
    keywords = await extractor.extract(text)
    print(f"Keywords: {keywords}")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
