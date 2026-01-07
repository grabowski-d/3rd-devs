"""Demo application for embeddings and vector search."""
import asyncio
from openai_service import OpenAIService
from text_service import TextSplitter
from vector_service import VectorService


COLLECTION_NAME = 'aidevs'

DATA = [
    'Apple (Consumer Electronics)',
    'Tesla (Automotive)',
    'Microsoft (Software)',
    'Google (Internet Services)',
    'Nvidia (Semiconductors)',
    'Meta (Social Media)',
    'X Corp (Social Media)',
    'Tech•sistence (Newsletter)'
]

QUERIES = ['Car company', 'Macbooks', 'Facebook', 'Newsletter']


async def initialize_data(openai_service: OpenAIService, vector_service: VectorService):
    """Initialize vector database with data."""
    text_splitter = TextSplitter()
    
    points = []
    for text in DATA:
        doc = await text_splitter.document(text, 'gpt-4', {'role': 'embedding-test'})
        points.append({
            'text': doc.text,
            'metadata': doc.metadata
        })
    
    await vector_service.initialize_collection_with_data(COLLECTION_NAME, points)


async def main():
    """Run demo embedding and search."""
    openai_service = OpenAIService()
    vector_service = VectorService(openai_service)
    
    # Initialize data
    await initialize_data(openai_service, vector_service)
    
    # Perform searches
    print(f'Searching in collection: {COLLECTION_NAME}\n')
    for query in QUERIES:
        results = await vector_service.perform_search(COLLECTION_NAME, query, limit=3)
        
        print(f'Query: {query}')
        for i, result in enumerate(results, 1):
            text = result['payload'].get('text', 'N/A')
            score = result.get('score', 0)
            print(f'  {i}. {text} (Score: {score:.4f})')
        print()


if __name__ == '__main__':
    asyncio.run(main())
