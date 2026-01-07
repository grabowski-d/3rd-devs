"""Flask Streaming App - Python implementation of streaming/app.ts"""
from flask import Flask, request, jsonify, Response
from openai_service import OpenAIService
from helpers import is_valid_message
import uuid
import json
import time

app = Flask(__name__)
app.json.compact = False

openai_service = OpenAIService()

def _validate_messages(req_data):
    messages = req_data.get('messages', [])
    if not isinstance(messages, list) or len(messages) == 0:
        raise ValueError('Invalid or missing messages in request body')
    if not all(is_valid_message(msg) for msg in messages):
        raise ValueError('Invalid message format in request body')
    return messages

@app.route('/api/chat', methods=['POST'])
async def chat():
    try:
        data = request.get_json()
        messages = _validate_messages(data)
        stream = data.get('stream', False)
        
        system_prompt = {"role": "system", "content": "You are a helpful assistant who speaks using as fewest words as possible."}
        await completion([system_prompt, *messages], stream)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as error:
        print(f'Error in OpenAI completion: {str(error)}')
        return jsonify({'error': 'An error occurred while processing your request'}), 500

async def completion(messages, stream: bool):
    conversation_uuid = str(uuid.uuid4())
    
    if stream:
        def generate():
            try:
                starting_chunk = {
                    'id': f"chatcmpl-{int(time.time() * 1000)}",
                    'object': 'chat.completion.chunk',
                    'created': int(time.time()),
                    'model': 'gpt-4',
                    'system_fingerprint': f"fp_{uuid.uuid4().hex[:15]}",
                    'choices': [{
                        'index': 0,
                        'delta': {'role': 'assistant', 'content': 'starting response'},
                        'logprobs': None,
                        'finish_reason': None
                    }]
                }
                yield f"data: {json.dumps(starting_chunk)}\n\n"
                
                result = await openai_service.completion(messages, "gpt-4", True)
                for chunk in result:
                    yield f"data: {json.dumps(chunk)}\n\n"
                    
            except Exception as error:
                print(f'Error in streaming response: {error}')
                error_chunk = {
                    'id': f"chatcmpl-{int(time.time() * 1000)}",
                    'object': 'chat.completion.chunk',
                    'created': int(time.time()),
                    'model': 'gpt-4',
                    'system_fingerprint': f"fp_{uuid.uuid4().hex[:15]}",
                    'choices': [{
                        'index': 0,
                        'delta': {'content': 'An error occurred during streaming'},
                        'logprobs': None,
                        'finish_reason': 'stop'
                    }]
                }
                yield f"data: {json.dumps(error_chunk)}\n\n"
        
        return Response(generate(), mimetype='text/event-stream', headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Conversation-UUID': conversation_uuid
        })
    else:
        answer = await openai_service.completion(messages)
        return jsonify({**answer, 'conversationUUID': conversation_uuid})

if __name__ == '__main__':
    print(f"Server running at http://localhost:5000. Listening for POST /api/chat requests")
    app.run(debug=True, port=5000)
