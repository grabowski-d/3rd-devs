"""Agent service for autonomous task execution."""
import json
import uuid as uuid_lib
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from openai.types.chat import ChatCompletionMessageParam, ChatCompletion
from .openai_service import OpenAIService
from .web_search import WebSearchService
from .text_service import TextService, IDoc


@dataclass
class AgentAction:
    """Record of an action taken by the agent."""
    uuid: str
    name: str
    parameters: str
    description: str
    results: List[IDoc] = field(default_factory=list)
    tool_uuid: str = ''


@dataclass
class AgentConfig:
    """Agent configuration."""
    active_step: Optional[Dict[str, str]] = None


@dataclass
class AgentState:
    """Agent state tracking."""
    messages: List[ChatCompletionMessageParam] = field(default_factory=list)
    tools: List[Dict[str, str]] = field(default_factory=list)
    actions: List[AgentAction] = field(default_factory=list)
    documents: List[IDoc] = field(default_factory=list)
    config: AgentConfig = field(default_factory=AgentConfig)


class Agent:
    """Autonomous agent for task execution with planning and web search."""

    def __init__(self, state: AgentState):
        """Initialize agent.
        
        Args:
            state: Initial agent state.
        """
        self.openai_service = OpenAIService()
        self.web_search_service = WebSearchService()
        self.text_service = TextService()
        self.state = state

    async def plan(self) -> Optional[Dict[str, str]]:
        """Plan the next action based on current state.
        
        Returns:
            Dict with 'tool' and 'query' keys, or None if planning fails.
        """
        tools_str = ', '.join(t.get('name', '') for t in self.state.tools)
        actions_str = '\n'.join(
            f'- {a.name}: {a.description}'
            for a in self.state.actions
        ) or 'No actions taken yet'

        system_message: ChatCompletionMessageParam = {
            'role': 'system',
            'content': f'''Analyze the conversation and determine the most appropriate next step.

Available tools: {tools_str}
Actions taken: {actions_str}
Current date: {__import__("datetime").datetime.now().isoformat()}
Last message: "{self.state.messages[-1]['content'] if self.state.messages else 'No messages'}"

Respond with JSON:
{{
    "_reasoning": "why this action is best",
    "tool": "tool_name",
    "query": "what needs to be done"
}}

Or if you have sufficient information:
{{
    "tool": "final_answer",
    "query": "your response"
}}
'''
        }

        try:
            response = await self.openai_service.completion({
                'messages': [system_message],
                'model': 'gpt-4o',
                'stream': False,
                'jsonMode': True,
            })

            if isinstance(response, ChatCompletion):
                content = response.choices[0].message.content
                if content:
                    result = json.loads(content)
                    return result if result.get('tool') else None
        except Exception as e:
            print(f'Error in plan: {e}')

        return None

    async def describe(
        self,
        tool: str,
        query: str
    ) -> Dict[str, Any]:
        """Generate specific parameters for a tool.
        
        Args:
            tool: Tool name.
            query: User query.
        
        Returns:
            Dict with tool-specific parameters.
        """
        tool_info = next((t for t in self.state.tools if t.get('name') == tool), None)
        if not tool_info:
            raise ValueError(f'Tool {tool} not found')

        system_message: ChatCompletionMessageParam = {
            'role': 'system',
            'content': f'''Generate specific parameters for the "{tool}" tool.

Tool description: {tool_info.get('description')}
Required parameters: {tool_info.get('parameters')}
Original query: {query}
Last message: "{self.state.messages[-1]['content'] if self.state.messages else ''}" 
Previous actions: {', '.join(f"{a.name}" for a in self.state.actions)}

Respond with ONLY a JSON object matching the tool's parameter structure.
'''
        }

        try:
            response = await self.openai_service.completion({
                'messages': [system_message],
                'model': 'gpt-4o',
                'stream': False,
                'jsonMode': True,
            })

            if isinstance(response, ChatCompletion):
                content = response.choices[0].message.content
                if content:
                    return json.loads(content)
        except Exception as e:
            print(f'Error in describe: {e}')

        return {}

    async def use_tool(
        self,
        tool: str,
        parameters: Dict[str, Any],
        conversation_uuid: str
    ) -> None:
        """Execute a tool with given parameters.
        
        Args:
            tool: Tool name.
            parameters: Tool parameters.
            conversation_uuid: Conversation ID.
        """
        if tool == 'web_search':
            results = await self.web_search_service.search(
                parameters.get('query', ''),
                conversation_uuid
            )
            # Filter to complete/non-chunk results
            self.state.documents.extend([
                r for r in results
                if r.metadata.content_type != 'chunk'
            ])
            self.state.actions.append(AgentAction(
                uuid=str(uuid_lib.uuid4()),
                name=tool,
                parameters=json.dumps(parameters),
                description=f'Search results for "{parameters.get("query")}"',
                results=results,
                tool_uuid=tool,
            ))

    async def generate_answer(
        self,
        context: Optional[List[IDoc]] = None,
        query: Optional[str] = None
    ) -> ChatCompletion:
        """Generate final answer based on gathered context.
        
        Args:
            context: Optional context documents.
            query: Optional query to answer.
        
        Returns:
            ChatCompletion response.
        """
        if context is None:
            context = [r for a in self.state.actions for r in a.results]
        if query is None:
            query = self.state.config.active_step.get('query', '') if self.state.config.active_step else ''

        context_str = '\n\n'.join(
            f"# {c.metadata.name or c.metadata.source}\n{c.text}"
            for c in context
        )

        system_message: ChatCompletionMessageParam = {
            'role': 'system',
            'content': f'''You are a helpful assistant. Use the provided context to answer the query.

Context:
{context_str}

Query: {query}

Provide a comprehensive answer based on the context.
'''
        }

        response = await self.openai_service.completion({
            'messages': [system_message, *self.state.messages],
            'model': 'gpt-4o',
            'stream': False,
        })

        return response
