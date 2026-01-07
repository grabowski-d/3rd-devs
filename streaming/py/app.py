"""Flask application for streaming chat."""
from flask import Flask, request, jsonify, Response, stream_with_context
import asyncio
from openai_service import OpenAIService
from streaming_service import StreamingService
from helpers import validate_messages

app = Flask(__name__)
port = 3000

openai_service = OpenAIService()
streaming_service = StreamingService(openai_service)


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat endpoint with optional streaming."""
    data = request.json
    messages = data.get('messages', [])
    stream = data.get('stream', False)

    # Validate messages
    if not validate_messages(messages):
        return jsonify({'error': 'Invalid or missing messages in request body'}), 400

    try:
        async def generate():
            async for chunk in streaming_service.completion(messages, stream):
                yield chunk

        if stream:
            return Response(
                stream_with_context(generate()),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'X-Accel-Buffering': 'no',
                }
            )
        else:
            # For non-streaming, collect response
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response_data = None
                async def collect():
                    nonlocal response_data
                    async for chunk in streaming_service.completion(messages, False):
                        response_data = chunk
                
                loop.run_until_complete(collect())
                import json
                return jsonify(json.loads(response_data))
            finally:
                loop.close()

    except Exception as error:
        return jsonify({'error': f'Error processing request: {error}'}), 500


if __name__ == '__main__':
    print(f'Server running at http://localhost:{port}. Listening for POST /api/chat requests')
    app.run(port=port, debug=False, threaded=True)
