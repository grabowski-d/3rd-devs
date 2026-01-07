"""Demo RAG application."""
import asyncio
from openai_service import OpenAIService
from text_service import TextSplitter
from vector_service import VectorService


COLLECTION_NAME = 'aidevs'

DATA = [
    'Good to Great: "Good is the enemy of great. To go from good to great requires transcending the curse of competence."',
    'Built to Last: "Clock building, not time telling. Focus on building an organization that can prosper far beyond the presence of any single leader and through multiple product life cycles."',
    'Great by Choice: "20 Mile March. Achieve consistent performance markers, in good times and bad, as a way to build resilience and maintain steady growth."',
    'How the Mighty Fall: "Five stages of decline: hubris born of success, undisciplined pursuit of more, denial of risk and peril, grasping for salvation, and capitulation to irrelevance or death."',
    'Beyond Entrepreneurship 2.0: "The flywheel effect. Success comes from consistently pushing in a single direction, gaining momentum over time."',
    'Turning the Flywheel: "Disciplined people, thought, and action. Great organizations are built on a foundation of disciplined individuals who engage in disciplined thought and take disciplined action."',
    'Built to Last: "Preserve the core, stimulate progress. Enduring great companies maintain their core values and purpose while their business strategies and operating practices endlessly adapt to a changing world."',
    'Good to Great: "First who, then what. Get the right people on the bus, the wrong people off the bus, and the right people in the right seats before you figure out where to drive it."',
    'Start with Why: "People don\'t buy what you do; they buy why you do it. And what you do simply proves what you believe."',
    'Leaders Eat Last: "The true price of leadership is the willingness to place the needs of others above your own. Great leaders truly care about those they are privileged to lead and understand that the true cost of the leadership privilege comes at the expense of self-interest."',
    'The Infinite Game: "In the Infinite Game, the true value of an organization cannot be measured by the success it has achieved based on a set of arbitrary metrics over arbitrary time frames."'
]

QUERIES = ['What does Sinek said about working with people?']


async def initialize_data(openai_service: OpenAIService, vector_service: VectorService):
    """Initialize RAG database."""
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
    """Run RAG demo."""
    openai_service = OpenAIService()
    vector_service = VectorService(openai_service)
    
    await initialize_data(openai_service, vector_service)
    
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
