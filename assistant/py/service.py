"""Assistant service implementing thinking-planning-action loop for AI agents."""

import json
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from .openai_service import OpenAIService
from .types import (
    Action,
    ActionResult,
    Config,
    Memory,
    MessageParam,
    State,
    Task,
    Thoughts,
    Tool,
)


class AssistantService:
    """Service for managing AI agent with thinking-planning-action loop.

    Implements a sophisticated agent architecture with three main phases:
    1. Thinking: Analyze environment, personality, memory, and available tools
    2. Planning: Create tasks and plan actions to accomplish goals
    3. Action: Execute planned actions and handle results
    """

    def __init__(self, openai_service: Optional[OpenAIService] = None):
        """Initialize AssistantService.

        Args:
            openai_service: OpenAI service instance. Creates new if not provided.
        """
        self.openai = openai_service or OpenAIService()
        self.tool_handlers: Dict[str, Callable] = {}

    def register_tool_handler(
        self, tool_name: str, handler: Callable[[Dict[str, Any]], Dict[str, Any]]
    ) -> None:
        """Register a handler for a specific tool.

        Args:
            tool_name: Name of the tool to handle.
            handler: Callable that processes the tool.
        """
        self.tool_handlers[tool_name] = handler

    async def thinking_phase(
        self, state: State, user_message: str
    ) -> Dict[str, str]:
        """Execute thinking phase to analyze context.

        Analyzes:
        - Environment: Current context and surroundings
        - Personality: Agent personality and traits
        - Memory: Relevant memories and past experiences
        - Tools: Available tools and their usage

        Args:
            state: Current agent state.
            user_message: User's input message.

        Returns:
            Dictionary with thinking results.
        """
        try:
            # Simplified thinking prompts
            environment_prompt = f"Analyze the current environment: {state['config']['environment']}"
            personality_prompt = f"Consider personality: {state['config']['personality']}"
            memory_prompt = f"Recall relevant memories for: {user_message}"
            tools_prompt = f"Identify tools needed for: {user_message}"

            results = {
                "environment": environment_prompt,
                "personality": personality_prompt,
                "memory": memory_prompt,
                "tools": tools_prompt,
            }

            print("\n=== Thinking Phase Results ===")
            for key, value in results.items():
                print(f"{key.capitalize()}: {value}")

            state["thoughts"] = results  # type: ignore
            return results

        except Exception as error:
            print(f"Error in thinking phase: {error}")
            raise

    async def planning_phase(self, state: State, user_message: str) -> None:
        """Execute planning phase to create tasks and actions.

        Args:
            state: Current agent state.
            user_message: User's input message.
        """
        try:
            # Create initial task
            task: Task = {
                "uuid": str(uuid.uuid4()),
                "conversation_uuid": str(uuid.uuid4()),
                "status": "pending",
                "name": f"Task for: {user_message[:50]}",
                "description": user_message,
                "actions": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            # Create initial action
            action: Action = {
                "uuid": str(uuid.uuid4()),
                "task_uuid": task["uuid"],
                "name": "Analyze user request",
                "tool_name": "memory",
                "payload": {"query": user_message},
                "result": None,
                "status": "pending",
                "sequence": 0,
                "description": "Analyze and plan response",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            task["actions"].append(action)
            state["tasks"].append(task)
            state["config"]["task"] = task["uuid"]
            state["config"]["action"] = action["uuid"]

            print("\n=== Planning Phase Results ===")
            print(f"Task: {task['name']}")
            print(f"Action: {action['name']}")

        except Exception as error:
            print(f"Error in planning phase: {error}")
            raise

    async def action_phase(self, state: State, user_message: str) -> None:
        """Execute action phase to run planned actions.

        Args:
            state: Current agent state.
            user_message: User's input message.
        """
        try:
            current_task_uuid = state["config"]["task"]
            current_action_uuid = state["config"]["action"]

            if not current_task_uuid or not current_action_uuid:
                return

            # Find current task and action
            current_task = next(
                (t for t in state["tasks"] if t["uuid"] == current_task_uuid), None
            )
            if not current_task:
                return

            current_action = next(
                (a for a in current_task["actions"] if a["uuid"] == current_action_uuid),
                None,
            )
            if not current_action:
                return

            # Execute tool if handler exists
            tool_name = current_action["tool_name"]
            if tool_name in self.tool_handlers:
                result = self.tool_handlers[tool_name](current_action["payload"])
                current_action["result"] = result
                current_action["status"] = "completed"

            print("\n=== Action Phase Results ===")
            print(f"Tool: {tool_name}")
            print(f"Result: {current_action['result']}")

        except Exception as error:
            print(f"Error in action phase: {error}")
            raise

    async def execute_loop(
        self, state: State, user_message: str, max_iterations: int = 3
    ) -> State:
        """Execute complete thinking-planning-action loop.

        Args:
            state: Initial agent state.
            user_message: User's input message.
            max_iterations: Maximum loop iterations.

        Returns:
            Updated state after execution.
        """
        state["config"]["step"] = 0
        state["messages"].append({"role": "user", "content": user_message})

        # Thinking phase
        await self.thinking_phase(state, user_message)

        # Planning and action loop
        while state["config"]["step"] < max_iterations:
            print(f"\n=== Step {state['config']['step'] + 1} ===")

            await self.planning_phase(state, user_message)
            await self.action_phase(state, user_message)

            # Check if we should continue
            current_task_uuid = state["config"]["task"]
            if not current_task_uuid:
                break

            current_task = next(
                (t for t in state["tasks"] if t["uuid"] == current_task_uuid), None
            )
            if current_task:
                current_task["status"] = "completed"

            state["config"]["step"] += 1

        print("\n=== Loop Complete ===")
        return state
