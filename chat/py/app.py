"""Flask Chat App - Python implementation of chat/app.ts"""
from flask import Flask, request, jsonify
from openai_service import OpenAIService

app = Flask(__name__)
app.json.compact = False

openai_service = OpenAIService()
previous_summarization = ""

async def generate_summarization(user_message: dict, assistant_response: dict) -> str:
    global previous_summarization
    current_turn = f"Adam: {user_message.get('content')}\nAlice: {assistant_response.get('content')}"
    
    summarization_prompt = {
        "role": "system",
        "content": f"""Please summarize the following conversation in a concise manner, incorporating the previous summary if available:

Previous summary: {previous_summarization or 'No previous summary'}

Current turn:
{current_turn}

Adam: Please update our conversation summary."""
    }
    
    response = await openai_service.completion([summarization_prompt], "gpt-4o", False)
    return response.get('choices', [{}])[0].get('message', {}).get('content', 'No conversation history')

def create_system_prompt(summarization: str) -> dict:
    return {
        "role": "system",
        "content": f"""You are Alice, a helpful assistant who speaks using as few words as possible.
        {'Here is a summary of the conversation so far: <summary>' + summarization + '</summary>' if summarization else ''}
        Let's chat!"""
    }

@app.route('/api/chat', methods=['POST'])
async def chat():
    global previous_summarization
    data = request.get_json()
    message = data.get('message')
    
    try:
        system_prompt = create_system_prompt(previous_summarization)
        assistant_response = await openai_service.completion([system_prompt, message], "gpt-4o", False)
        previous_summarization = await generate_summarization(message, assistant_response.get('choices', [{}])[0].get('message'))
        return jsonify(assistant_response)
    except Exception as error:
        print(f'Error in OpenAI completion: {str(error)}')
        return jsonify({'error': 'An error occurred while processing your request'}), 500

@app.route('/api/demo', methods=['POST'])
async def demo():
    global previous_summarization
    demo_messages = [
        {"content": "Hi! I'm Adam", "role": "user"},
        {"content": "How are you?", "role": "user"},
        {"content": "Do you know my name?", "role": "user"}
    ]
    
    assistant_response = None
    for message in demo_messages:
        print('--- NEXT TURN ---')
        print(f"Adam: {message.get('content')}")
        
        try:
            system_prompt = create_system_prompt(previous_summarization)
            assistant_response = await openai_service.completion([system_prompt, message], "gpt-4o", False)
            print(f"Alice: {assistant_response.get('choices', [{}])[0].get('message', {}).get('content')}")
            previous_summarization = await generate_summarization(message, assistant_response.get('choices', [{}])[0].get('message'))
        except Exception as error:
            print(f'Error in OpenAI completion: {str(error)}')
            return jsonify({'error': 'An error occurred while processing your request'}), 500
    
    return jsonify(assistant_response)

if __name__ == '__main__':
    print(f"Server running at http://localhost:5000. Listening for POST /api/chat requests")
    app.run(debug=True, port=5000)
