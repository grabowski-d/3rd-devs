"""Assistant service with multi-tool orchestration."""
import json
from typing import Dict, Any, List, Optional
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam
from .openai_service import OpenAIService


class AssistantService:
    """Orchestrates multiple tools via function calling."""

    def __init__(self, config: Dict[str, str]):
        """Initialize assistant service.
        
        Args:
            config: Configuration dict with API keys for various services.
        """
        self.openai_service = OpenAIService()
        self.config = config
        self.tools = self._define_tools()

    def _define_tools(self) -> List[ChatCompletionToolParam]:
        """Define available tools for function calling.
        
        Returns:
            List of tool definitions.
        """
        return [
            {
                'type': 'function',
                'function': {
                    'name': 'search_music',
                    'description': 'Search for music on Spotify',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'query': {
                                'type': 'string',
                                'description': 'Search query for music'
                            },
                            'limit': {
                                'type': 'integer',
                                'description': 'Maximum number of results',
                                'default': 5
                            }
                        },
                        'required': ['query']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'play_music',
                    'description': 'Play music on Spotify',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'query': {
                                'type': 'string',
                                'description': 'Music to play'
                            }
                        },
                        'required': ['query']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'get_directions',
                    'description': 'Get directions between two locations',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'origin': {
                                'type': 'string',
                                'description': 'Starting location'
                            },
                            'destination': {
                                'type': 'string',
                                'description': 'Destination location'
                            },
                            'mode': {
                                'type': 'string',
                                'description': 'Travel mode (driving, walking, transit)',
                                'default': 'driving'
                            }
                        },
                        'required': ['origin', 'destination']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'send_email',
                    'description': 'Send an email',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'to': {
                                'type': 'string',
                                'description': 'Recipient email address'
                            },
                            'subject': {
                                'type': 'string',
                                'description': 'Email subject'
                            },
                            'body': {
                                'type': 'string',
                                'description': 'Email body content'
                            }
                        },
                        'required': ['to', 'subject', 'body']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'search_youtube',
                    'description': 'Search YouTube videos',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'query': {
                                'type': 'string',
                                'description': 'Search query'
                            },
                            'max_results': {
                                'type': 'integer',
                                'description': 'Max results',
                                'default': 5
                            }
                        },
                        'required': ['query']
                    }
                }
            }
        ]

    async def process_request(
        self,
        user_message: str,
        conversation_history: Optional[List[ChatCompletionMessageParam]] = None
    ) -> Dict[str, Any]:
        """Process user request with function calling.
        
        Args:
            user_message: User's request.
            conversation_history: Previous messages.
        
        Returns:
            Dict with response and any tool calls.
        """
        messages = conversation_history or []
        messages.append({
            'role': 'user',
            'content': user_message
        })
        
        # Get initial response with function calling
        response = await self.openai_service.completion(
            messages=messages,
            model='gpt-4o',
            tools=self.tools,
            tool_choice='auto'
        )
        
        # Extract tool calls
        tool_calls = await self.openai_service.extract_tool_calls(response)
        
        return {
            'response': response,
            'tool_calls': tool_calls,
            'content': response.choices[0].message.content if response.choices else None
        }

    async def execute_tool(
        self,
        tool_name: str,
        arguments: str
    ) -> Dict[str, Any]:
        """Execute a tool with given arguments.
        
        Args:
            tool_name: Name of the tool to execute.
            arguments: JSON string of tool arguments.
        
        Returns:
            Tool execution result.
        """
        try:
            args = json.loads(arguments)
        except json.JSONDecodeError:
            return {'error': 'Invalid arguments JSON'}
        
        # Map tool names to implementations
        if tool_name == 'search_music':
            return await self._search_music(args)
        elif tool_name == 'play_music':
            return await self._play_music(args)
        elif tool_name == 'get_directions':
            return await self._get_directions(args)
        elif tool_name == 'send_email':
            return await self._send_email(args)
        elif tool_name == 'search_youtube':
            return await self._search_youtube(args)
        else:
            return {'error': f'Unknown tool: {tool_name}'}

    async def _search_music(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search for music. Implementation stub."""
        query = args.get('query')
        limit = args.get('limit', 5)
        return {
            'status': 'success',
            'query': query,
            'limit': limit,
            'results': [
                {'title': f'Result {i+1} for {query}', 'artist': 'Artist'}
                for i in range(limit)
            ]
        }

    async def _play_music(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Play music. Implementation stub."""
        query = args.get('query')
        return {
            'status': 'success',
            'action': 'playing',
            'query': query,
            'message': f'Now playing: {query}'
        }

    async def _get_directions(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get directions. Implementation stub."""
        origin = args.get('origin')
        destination = args.get('destination')
        mode = args.get('mode', 'driving')
        return {
            'status': 'success',
            'origin': origin,
            'destination': destination,
            'mode': mode,
            'distance': '10 km',
            'duration': '15 mins'
        }

    async def _send_email(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Send email. Implementation stub."""
        to = args.get('to')
        subject = args.get('subject')
        return {
            'status': 'success',
            'to': to,
            'subject': subject,
            'message': f'Email sent to {to}'
        }

    async def _search_youtube(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search YouTube. Implementation stub."""
        query = args.get('query')
        max_results = args.get('max_results', 5)
        return {
            'status': 'success',
            'query': query,
            'results': [
                {'title': f'Video {i+1} about {query}', 'channel': 'Channel'}
                for i in range(max_results)
            ]
        }
