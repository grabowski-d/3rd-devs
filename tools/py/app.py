"""Demo app for function calling tools."""
import asyncio
from assistant_service import AssistantService
from openai_service import OpenAIService


async def main():
    """Run function calling demo."""
    config = {
        'spotify_client_id': '',
        'spotify_client_secret': '',
        'youtube_api_key': '',
        'google_maps_api_key': '',
        'calendar_client_id': '',
        'calendar_client_secret': '',
        'resend_api_key': ''
    }
    
    assistant = AssistantService(config)
    
    # Test various requests
    test_requests = [
        'Play some relaxing music',
        'Get directions from New York to Boston',
        'Send me an email reminder about the meeting',
        'Search for Python tutorials on YouTube'
    ]
    
    for request in test_requests:
        print(f'\nUser: {request}')
        print('-' * 50)
        
        result = await assistant.process_request(request)
        
        if result.get('tool_calls'):
            print(f'Tools called: {len(result["tool_calls"])}')
            for call in result['tool_calls']:
                print(f'  - {call["name"]}: {call["arguments"]}')
        
        if result.get('content'):
            print(f'Assistant: {result["content"]}')


if __name__ == '__main__':
    asyncio.run(main())
