"""Service for chat conversations with summarization."""
from typing import List, Optional, Dict, Any
from openai.types.chat import ChatCompletionMessageParam, ChatCompletion
from openai import OpenAI


class ChatService:
    """Service for managing chat conversations with summarization."""

    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize chat service.
        
        Args:
            openai_api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var.
        """
        self.client = OpenAI(api_key=openai_api_key)
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
        current_turn = f"Adam: {user_message.get('content', '')}"
        current_turn += f"""{assistant_response.get('content', '')}"""

        summarization_prompt: ChatCompletionMessageParam = {
            'role': 'system',
            'content': f'''Please summarize the following conversation in a concise manner,
incorporating the previous summary if available:

Previous summary: {self.previous_summarization or "No previous summary"}

Current turn:
{current_turn}

Adam: Please update our conversation summary.'''
        }

        response = self.client.chat.completions.create(
            messages=[summarization_prompt],
            model='gpt-4o',
            stream=False,
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
<summary>{summarization}</summary>'''
        
        content += '\n\nLet\'s chat!'
        
        return {'role': 'system', 'content': content}

    async def chat(self, message: Dict[str, str]) -> ChatCompletion:
        """Handle single chat message.
        
        Args:
            message: Message dict with 'content' key.
        
        Returns:
            ChatCompletion response.
        """
        user_msg: ChatCompletionMessageParam = {
            'role': 'user',
            'content': message.get('message', '')
        }
        
        system_prompt = self.create_system_prompt(self.previous_summarization)
        
        response = self.client.chat.completions.create(
            messages=[system_prompt, user_msg],
            model='gpt-4o',
            stream=False,
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
        
        return response

    async def demo(self) -> Optional[ChatCompletion]:
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

            system_prompt = self.create_system_prompt(self.previous_summarization)
            
            response = self.client.chat.completions.create(
                messages=[system_prompt, message],
                model='gpt-4o',
                stream=False,
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

        return assistant_response
