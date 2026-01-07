"""Main Flask App - Python implementation of database/app.ts"""
import uuid
from flask import Flask, request, jsonify
from database_service import DatabaseService
from langfuse_service import LangfuseService
from openai_service import OpenAIService
from assistant_service import AssistantService

app = Flask(__name__)
app.json.compact = False

database_service = DatabaseService()
langfuse_service = LangfuseService()
openai_service = OpenAIService()
assistant_service = AssistantService(database_service, openai_service, langfuse_service)

@app.route('/api/chat', methods=['POST'])
async def chat():
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        conversation_id = data.get('conversation_id', str(uuid.uuid4()))
        messages = [msg for msg in messages if msg.get('role') != 'system']
        
        last_content = (messages[-1].get('content', '') if messages else '')[:45]
        trace = langfuse_service.create_trace({'id': str(uuid.uuid4()), 'name': last_content, 'sessionId': conversation_id, 'userId': 'test-user'})
        
        answer = await assistant_service.answer({'messages': messages, 'conversation_id': conversation_id}, trace)
        await langfuse_service.finalize_trace(trace, messages, answer.get('choices', [{}])[0].get('message'))
        await langfuse_service.flush_async()
        
        return jsonify({**answer, 'conversation_id': conversation_id})
    except Exception as error:
        print(f'Error in chat processing: {error}')
        return jsonify({'error': 'An error occurred while processing your request'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    import signal, sys
    signal.signal(signal.SIGINT, lambda sig, frame: (print("Shutting down..."), sys.exit(0)))
    print("Server running at http://localhost:5000")
    app.run(debug=True, port=5000)
