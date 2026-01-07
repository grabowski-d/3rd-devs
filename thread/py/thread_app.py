"""Express-like Flask application for thread conversations."""
import asyncio
from typing import Dict, Any, Optional, List
from openai.types.chat import ChatCompletionMessageParam, ChatCompletion
from openai import OpenAI
from .openai_service import OpenAIService


class ThreadApp:
    """Thread conversation application with summarization."""

    def __init__(self, port: int = 3000):
        """Initialize thread app.
        
        Args:
            port: Port to listen on.
        """
        self.port = port
        self.openai_service = OpenAIService()
        self.previous_summarization = ""

    async def generate_summarization(
        self,
        user_message: ChatCompletionMessageParam,
        assistant_response: ChatCompletionMessageParam
    ) -> str:
        """Generate updated conversation summary.
        
        Args:
            user_message: User's message.
            assistant_response: Assistant's response.
        
        Returns:
            Updated conversation summary.
        """
        summarization_prompt: ChatCompletionMessageParam = {
            'role': 'system',
            'content': f'''Please summarize the following conversation in a concise manner, 
incorporating the previous summary if available:
<previous_summary>{self.previous_summarization or "No previous summary"}</previous_summary>
<current_turn>
User: {user_message.get('content', '')}
Assistant: {assistant_response.get('content', '')}
</current_turn>
'''
        }

        response = await self.openai_service.completion(
            [summarization_prompt, {'role': 'user', 'content': 'Please create/update our conversation summary.'}],
            'gpt-4o-mini',
            False
        )

        if isinstance(response, ChatCompletion):
            return response.choices[0].message.content or 'No conversation history'
        return 'Error generating summary'

    def create_system_prompt(self, summarization: str) -> ChatCompletionMessageParam:
        """Create system prompt with conversation context.
        
        Args:
            summarization: Conversation summary.
        
        Returns:
            System message with context.
        """
        content = '''You are Alice, a helpful assistant who speaks using as few words as possible.
'''
        
        if summarization:
            content += f'''\nHere is a summary of the conversation so far:
<conversation_summary>
{summarization}
</conversation_summary>'''
        
        content += '\n\nLet\'s chat!'
        
        return {'role': 'system', 'content': content}

    async def handle_chat(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chat message.
        
        Args:
            message: User message dict with 'content' key.
        
        Returns:
            Assistant response.
        """
        try:
            user_msg: ChatCompletionMessageParam = {
                'role': 'user',
                'content': message.get('message', '')
            }
            
            system_prompt = self.create_system_prompt(self.previous_summarization)
            
            response = await self.openai_service.completion(
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
            self.previous_summarization = await self.generate_summarization(
                user_msg,
                assistant_response
            )
            
            return response.model_dump()
        
        except Exception as error:
            raise ValueError(f'Error in chat processing: {error}')

    async def handle_demo(self) -> Optional[Dict[str, Any]]:
        """Run demo conversation.
        
        Returns:
            Final assistant response.
        """
        demo_messages: List[ChatCompletionMessageParam] = [
            {'content': "Hi! I'm Adam", 'role': 'user'},
            {'content': 'How are you?', 'role': 'user'},
            {'content': 'Do you know my name?', 'role': 'user'}
        ]

        assistant_response: Optional[ChatCompletion] = None

        for message in demo_messages:
            print(f'--- NEXT TURN ---')
            print(f"Adam: {message.get('content')}")

            try:
                system_prompt = self.create_system_prompt(self.previous_summarization)
                
                response = await self.openai_service.completion(
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
                self.previous_summarization = await self.generate_summarization(
                    message,
                    assistant_msg
                )
            
            except Exception as error:
                raise ValueError(f'Error in demo: {error}')

        return assistant_response.model_dump() if assistant_response else None

    # REST API endpoints
    def create_routes(self, app: Any) -> None:
        """Create Flask routes for the application.
        
        Args:
            app: Flask application instance.
        """
        @app.route('/api/chat', methods=['POST'])
        async def chat():
            from flask import request, jsonify
            try:
                data = request.json
                result = await self.handle_chat(data)
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/demo', methods=['POST'])
        async def demo():
            from flask import jsonify
            try:
                result = await self.handle_demo()
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
