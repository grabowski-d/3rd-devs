"""Flask application for chat conversations."""
from flask import Flask, request, jsonify
import asyncio
from chat_service import ChatService

app = Flask(__name__)
port = 3000

chat_service = ChatService()


@app.route('/api/chat', methods=['POST'])
async def chat():
    """Handle chat endpoint."""
    try:
        data = request.json
        result = await chat_service.chat(data)
        return jsonify(result.model_dump())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/demo', methods=['POST'])
async def demo():
    """Handle demo endpoint."""
    try:
        result = await chat_service.demo()
        return jsonify(result.model_dump() if result else {})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print(f'Server running at http://localhost:{port}. Listening for POST /api/chat and /api/demo requests')
    app.run(port=port, debug=False)
