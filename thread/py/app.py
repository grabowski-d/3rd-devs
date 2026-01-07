"""Flask application for thread conversations."""
from flask import Flask, request, jsonify
import asyncio
from openai.types.chat import ChatCompletionMessageParam, ChatCompletion
from openai_service import OpenAIService

app = Flask(__name__)
port = 3000

openai_service = OpenAIService()
previous_summarization = ""


async def generate_summarization(
    user_message: ChatCompletionMessageParam,
    assistant_response: ChatCompletionMessageParam
) -> str:
    """Generate updated conversation summary."""
    summarization_prompt: ChatCompletionMessageParam = {
        'role': 'system',
        'content': f'''Please summarize the following conversation in a concise manner,
incorporating the previous summary if available:
<previous_summary>{previous_summarization or "No previous summary"}</previous_summary>
<current_turn>
User: {user_message.get('content', '')}
Assistant: {assistant_response.get('content', '')}
</current_turn>
'''
    }

    response = await openai_service.completion(
        [summarization_prompt, {'role': 'user', 'content': 'Please create/update our conversation summary.'}],
        'gpt-4o-mini',
        False
    )

    if isinstance(response, ChatCompletion):
        return response.choices[0].message.content or 'No conversation history'
    return 'Error generating summary'


def create_system_prompt(summarization: str) -> ChatCompletionMessageParam:
    """Create system prompt with conversation context."""
    content = '''You are Alice, a helpful assistant who speaks using as few words as possible.
'''
    
    if summarization:
        content += f'''\nHere is a summary of the conversation so far:
<conversation_summary>
{summarization}
</conversation_summary>'''
    
    content += '\n\nLet\'s chat!'
    
    return {'role': 'system', 'content': content}


@app.route('/api/chat', methods=['POST'])
async def chat():
    """Handle chat endpoint."""
    global previous_summarization
    
    message = request.json.get('message', '')

    try:
        user_msg: ChatCompletionMessageParam = {
            'role': 'user',
            'content': message
        }
        
        system_prompt = create_system_prompt(previous_summarization)
        
        response = await openai_service.completion(
            [system_prompt, user_msg],
            'gpt-4o',
            False
        )

        if not isinstance(response, ChatCompletion):
            raise ValueError('Expected ChatCompletion, got streaming response')
        
        assistant_response: ChatCompletionMessageParam = {
            'role': 'assistant',
            'content': response.choices[0].message.content or ''
        }
        
        # Generate new summarization
        previous_summarization = await generate_summarization(
            user_msg,
            assistant_response
        )
        
        return jsonify(response.model_dump())
    
    except Exception as error:
        return jsonify({'error': f'Error in chat processing: {error}'}), 500


@app.route('/api/demo', methods=['POST'])
async def demo():
    """Handle demo endpoint."""
    global previous_summarization
    
    demo_messages = [
        {'content': "Hi! I'm Adam", 'role': 'user'},
        {'content': 'How are you?', 'role': 'user'},
        {'content': 'Do you know my name?', 'role': 'user'}
    ]

    assistant_response = None

    for message in demo_messages:
        print(f'--- NEXT TURN ---')
        print(f"Adam: {message.get('content')}")

        try:
            system_prompt = create_system_prompt(previous_summarization)
            
            response = await openai_service.completion(
                [system_prompt, message],
                'gpt-4o',
                False
            )

            if not isinstance(response, ChatCompletion):
                raise ValueError('Expected ChatCompletion')

            assistant_response = response
            print(f"Alice: {response.choices[0].message.content}")

            # Generate new summarization
            assistant_msg: ChatCompletionMessageParam = {
                'role': 'assistant',
                'content': response.choices[0].message.content or ''
            }
            previous_summarization = await generate_summarization(
                message,
                assistant_msg
            )
        
        except Exception as error:
            return jsonify({'error': f'Error in demo: {error}'}), 500

    return jsonify(assistant_response.model_dump() if assistant_response else {})


if __name__ == '__main__':
    print(f'Server running at http://localhost:{port}. Listening for POST /api/chat and /api/demo requests')
    app.run(port=port, debug=False)
