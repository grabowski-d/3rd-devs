"""Demo better RAG app."""
import asyncio
from openai_service import OpenAIService
from text_service import TextSplitter
from vector_service import VectorService
from rag_service import BetterRAGService

COLLECTION_NAME = 'aidevs_better'

DATA = [
    'Good to Great focuses on transcending competence through disciplined execution.',
    'Built to Last emphasizes clock building and organizational longevity.',
    'The hedgehog concept is central to sustainable competitive advantage.',
    'Culture of discipline drives exceptional performance.',
    'First who, then what - get the right people on the bus.'
]

async def main():
    openai_service = OpenAIService()
    vector_service = VectorService(openai_service)
    rag_service = BetterRAGService(openai_service, vector_service)
    text_splitter = TextSplitter()
    
    await vector_service.ensure_collection(COLLECTION_NAME)
    points = [{'text': t, 'metadata': {}} for t in DATA]
    await vector_service.add_points(COLLECTION_NAME, points)
    
    query = 'What does leadership mean?'
    results = await rag_service.search_with_expansion(COLLECTION_NAME, query, limit=3)
    print(f'Query: {query}\nResults:')
    for i, r in enumerate(results, 1):
        print(f'  {i}. {r["payload"].get("text")} (Score: {r["score"]:.4f})')

if __name__ == '__main__':
    asyncio.run(main())
