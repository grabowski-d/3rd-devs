"""Agent service for autonomous task execution."""
import json
from typing import Dict, Any, Optional, List
from uuid import uuid4
from openai.types.chat import ChatCompletionMessageParam

from .openai_service import OpenAIService
from .websearch_service import WebSearchService
from .types import State, Action, ActionResult


class AgentService:
    """Autonomous agent with planning and web search."""
    
    def __init__(self, state: State):
        """Initialize agent.
        
        Args:
            state: Initial agent state.
        """
        self.openai_service = OpenAIService()
        self.web_search_service = WebSearchService()
        self.state = state
    
    async def plan(self) -> Optional[Dict[str, Any]]:
        """Plan next action based on current state.
        
        Returns:
            Next action details or None.
        """
        system_message: ChatCompletionMessageParam = {
            'role': 'system',
            'content': f'''Analyze the conversation and determine the next action.

Context:
- Date: {__import__("datetime").datetime.now().isoformat()}
- Last message: "{self.state.messages[-1]["content"] if self.state.messages else "No messages"}"
- Available tools: {', '.join(t['name'] for t in self.state.tools)}
- Actions taken: {len(self.state.actions)}

Return JSON:
{{
  "_reasoning": "why this action",
  "tool": "tool_name",
  "query": "what to do"
}}

Or if done:
{{
  "_reasoning": "explanation",
  "tool": "final_answer",
  "query": "summary"
}}'''
        }
        
        response = await self.openai_service.completion(
            messages=[system_message],
            json_mode=True
        )
        
        try:
            result = json.loads(response.choices[0].message.content or '{}')
            return result if result.get('tool') else None
        except:
            return None
    
    async def describe(self, tool: str, query: str) -> Dict[str, Any]:
        """Generate parameters for tool execution.
        
        Args:
            tool: Tool name.
            query: Original query.
        
        Returns:
            Tool parameters.
        """
        tool_info = next((t for t in self.state.tools if t['name'] == tool), None)
        if not tool_info:
            raise ValueError(f'Tool {tool} not found')
        
        system_message: ChatCompletionMessageParam = {
            'role': 'system',
            'content': f'''Generate parameters for the "{tool}" tool.

Tool: {tool_info["name"]}
Description: {tool_info["description"]}
Parameters: {tool_info["parameters"]}

Respond with ONLY JSON matching the tool's parameter structure.'''
        }
        
        response = await self.openai_service.completion(
            messages=[system_message],
            json_mode=True
        )
        
        try:
            return json.loads(response.choices[0].message.content or '{}')
        except:
            return {}
    
    async def use_tool(self, tool: str, parameters: Dict[str, Any], conversation_uuid: str) -> None:
        """Execute tool and update state.
        
        Args:
            tool: Tool name.
            parameters: Tool parameters.
            conversation_uuid: Conversation UUID.
        """
        if tool == 'web_search':
            query = parameters.get('query', '')
            results = await self.web_search_service.search(query, conversation_uuid)
            
            # Convert IDoc to ActionResult
            action_results = [
                ActionResult(
                    text=doc.text,
                    metadata={
                        'name': doc.name,
                        'source': doc.source,
                        'urls': [doc.source]
                    }
                )
                for doc in results
            ]
            
            self.state.documents.extend(results)
            self.state.actions.append(Action(
                uuid=str(uuid4()),
                name=tool,
                parameters=json.dumps(parameters),
                description=f'Web search for: {query}',
                results=action_results,
                tool_uuid=tool
            ))
    
    async def generate_answer(self) -> str:
        """Generate final answer based on gathered information.
        
        Returns:
            Final answer.
        """
        context_text = '\n'.join([
            f'- {action.description}'
            for action in self.state.actions
        ])
        
        user_query = self.state.messages[-1]['content'] if self.state.messages else 'No query'
        
        system_message: ChatCompletionMessageParam = {
            'role': 'system',
            'content': f'''Provide a comprehensive answer based on the gathered information.

User query: {user_query}

Information gathered:
{context_text}

Provide a clear, well-structured answer.'''
        }
        
        response = await self.openai_service.completion(
            messages=[system_message] + self.state.messages
        )
        
        return response.choices[0].message.content or 'Unable to generate answer'
