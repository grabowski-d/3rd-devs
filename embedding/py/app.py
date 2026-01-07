"""Embedding Example App - Python implementation of embedding/app.ts"""
import asyncio
from openai_service import OpenAIService
from text_service import TextSplitter
from vector_service import VectorService

data = [
    'Apple (Consumer Electronics)',
    'Tesla (Automotive)',
    'Microsoft (Software)',
    'Google (Internet Services)',
    'Nvidia (Semiconductors)',
    'Meta (Social Media)',
    'X Corp (Social Media)',
    'Tech•sistence (Newsletter)'
]
queries = ['Car company', 'Macbooks', 'Facebook', 'Newsletter']

COLLECTION_NAME = "aidevs"

open_ai = OpenAIService()
vector_service = VectorService(open_ai)
text_splitter = TextSplitter()

async def initialize_data():
    points = []
    for text in data:
        doc = await text_splitter.document(text, 'gpt-4', {'role': 'embedding-test'})
        points.append(doc.__dict__ if hasattr(doc, '__dict__') else {'text': doc.text, 'metadata': doc.metadata})
    
    await vector_service.initialize_collection_with_data(COLLECTION_NAME, points)

async def main():
    await initialize_data()
    
    search_results = []
    for query in queries:
        result = await vector_service.perform_search(COLLECTION_NAME, query, 3)
        search_results.append(result)
    
    for query, results in zip(queries, search_results):
        print(f"Query: {query}")
        for idx, result in enumerate(results, 1):
            text = result.payload.get('text') if hasattr(result, 'payload') else result.get('text')
            score = result.score if hasattr(result, 'score') else result.get('score')
            print(f"  {idx}. {text} (Score: {score})")
        print()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as error:
        print(f"Error: {error}")
        import traceback
        traceback.print_exc()
