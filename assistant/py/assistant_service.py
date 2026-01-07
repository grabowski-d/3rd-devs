"""Assistant service with planning and reasoning capabilities."""

import logging
import json
from typing import Any, Callable, Dict, Optional
from uuid import uuid4
from datetime import datetime

from .types import (
    State,
    Config,
    Task,
    Action,
    ActionResult,
    Memory,
    Thoughts,
    Tool,
    MemoryCategory,
)
from .openai_service import OpenAIService

logger = logging.getLogger(__name__)


class AssistantService:
    """Assistant service for multi-phase reasoning and task execution."""

    def __init__(
        self,
        state: State,
        openai_service: Optional[OpenAIService] = None,
    ) -> None:
        """Initialize assistant service.

        Args:
            state: Initial assistant state
            openai_service: OpenAI service instance
        """
        self.state = state
        self.openai = openai_service or OpenAIService()
        self.tool_handlers: Dict[str, Callable] = {}
        
        logger.info(f"Initialized assistant: {state.config.ai_name}")

    def register_tool_handler(
        self, tool_name: str, handler: Callable[[Dict[str, Any]], ActionResult]
    ) -> None:
        """Register a tool handler.

        Args:
            tool_name: Name of the tool
            handler: Async function that takes payload dict and returns ActionResult
        """
        self.tool_handlers[tool_name] = handler
        logger.debug(f"Registered handler for tool: {tool_name}")

    async def thinking_phase(self, user_message: str) -> None:
        """Execute thinking phase.

        Analyzes context, personality, memory, and available tools.

        Args:
            user_message: The user's message
        """
        logger.info("Starting thinking phase")

        # Environment analysis
        env_response = await self.openai.completion(
            messages=[
                {"role": "system", "content": self._prompt_environment()},
                {"role": "user", "content": user_message},
            ],
            json_mode=True,
        )
        env_analysis = json.loads(env_response.choices[0].message.content or "{}")
        self.state.thoughts.environment = env_analysis.get("result", "")

        # Personality analysis
        pers_response = await self.openai.completion(
            messages=[
                {"role": "system", "content": self._prompt_personality()},
                {"role": "user", "content": user_message},
            ],
            json_mode=True,
        )
        pers_analysis = json.loads(pers_response.choices[0].message.content or "{}")
        self.state.thoughts.personality = pers_analysis.get("result", "")

        # Memory analysis
        mem_response = await self.openai.completion(
            messages=[
                {"role": "system", "content": self._prompt_memory()},
                {"role": "user", "content": user_message},
            ],
            json_mode=True,
        )
        mem_analysis = json.loads(mem_response.choices[0].message.content or "{}")
        self.state.thoughts.memory = mem_analysis.get("result", "")

        # Tools analysis
        tools_response = await self.openai.completion(
            messages=[
                {"role": "system", "content": self._prompt_tools()},
                {"role": "user", "content": user_message},
            ],
            json_mode=True,
        )
        tools_analysis = json.loads(tools_response.choices[0].message.content or "{}")
        self.state.thoughts.tools = tools_analysis.get("result", "")

        logger.debug("Thinking phase completed")

    async def planning_phase(self, user_message: str) -> None:
        """Execute planning phase.

        Creates tasks and actions from user request.

        Args:
            user_message: The user's message
        """
        logger.info("Starting planning phase")

        # Task planning
        task_response = await self.openai.completion(
            messages=[
                {"role": "system", "content": self._prompt_task()},
                {"role": "user", "content": user_message},
            ],
            json_mode=True,
        )
        task_analysis = json.loads(task_response.choices[0].message.content or "{}")
        tasks = task_analysis.get("result", [])

        # Update or create tasks
        updated_tasks = []
        for task_data in tasks:
            if "uuid" in task_data:
                # Update existing
                existing = next(
                    (t for t in self.state.tasks if t.uuid == task_data["uuid"]), None
                )
                if existing and existing.status == "pending":
                    existing.name = task_data.get("name", existing.name)
                    existing.description = task_data.get("description", existing.description)
                    existing.updated_at = datetime.now().isoformat()
                    updated_tasks.append(existing)
                elif existing:
                    updated_tasks.append(existing)
            else:
                # Create new
                updated_tasks.append(
                    Task(
                        uuid=str(uuid4()),
                        conversation_uuid=str(uuid4()),
                        name=task_data.get("name", "Untitled"),
                        description=task_data.get("description", ""),
                        status="pending",
                    )
                )

        self.state.tasks = updated_tasks

        # Set current task
        pending_task = next((t for t in self.state.tasks if t.status == "pending"), None)
        if pending_task:
            self.state.config.task = pending_task.uuid

        # Action planning
        action_response = await self.openai.completion(
            messages=[
                {"role": "system", "content": self._prompt_action()},
                {"role": "user", "content": user_message},
            ],
            json_mode=True,
        )
        action_analysis = json.loads(action_response.choices[0].message.content or "{}")
        action_data = action_analysis.get("result")

        if action_data:
            task_to_update = next(
                (t for t in self.state.tasks if t.uuid == action_data.get("task_uuid")),
                None,
            )
            if task_to_update:
                action = Action(
                    uuid=str(uuid4()),
                    task_uuid=task_to_update.uuid,
                    name=action_data.get("name", ""),
                    tool_name=action_data.get("tool_name", ""),
                    description=action_data.get("description", ""),
                )
                task_to_update.actions = [action]
                self.state.config.task = task_to_update.uuid
                self.state.config.action = action.uuid

        logger.debug("Planning phase completed")

    async def action_phase(self, user_message: str) -> None:
        """Execute action phase.

        Executes tools and handles results.

        Args:
            user_message: The user's message
        """
        if not self.state.config.task or not self.state.config.action:
            logger.warning("No task or action to execute")
            return

        logger.info("Starting action phase")

        # Get tool use prompt
        use_response = await self.openai.completion(
            messages=[
                {"role": "system", "content": self._prompt_use()},
                {"role": "user", "content": user_message},
            ],
            json_mode=True,
        )
        use_analysis = json.loads(use_response.choices[0].message.content or "{}")
        payload = use_analysis.get("result", {})

        # Get current action and execute
        task = next(
            (t for t in self.state.tasks if t.uuid == self.state.config.task), None
        )
        if task:
            action = next(
                (a for a in task.actions if a.uuid == self.state.config.action), None
            )
            if action:
                action.payload = payload

                # Execute tool
                handler = self.tool_handlers.get(action.tool_name)
                if handler:
                    action.result = await handler(payload)
                    logger.debug(f"Executed tool: {action.tool_name}")
                else:
                    logger.warning(f"No handler for tool: {action.tool_name}")

    async def execute_loop(self, user_message: str, max_steps: Optional[int] = None) -> State:
        """Execute the main assistant loop.

        Args:
            user_message: The user's message
            max_steps: Maximum steps (uses config.max_steps if not provided)

        Returns:
            Final state
        """
        if max_steps:
            self.state.config.max_steps = max_steps

        self.state.config.step = 0
        self.state.messages.append({"role": "user", "content": user_message})

        # Thinking phase
        await self.thinking_phase(user_message)

        # Main loop
        while self.state.config.step < self.state.config.max_steps:
            logger.info(f"Step {self.state.config.step + 1}/{self.state.config.max_steps}")

            await self.planning_phase(user_message)
            await self.action_phase(user_message)

            # Check if we should continue
            task = next(
                (t for t in self.state.tasks if t.uuid == self.state.config.task), None
            )
            action = (
                next((a for a in task.actions if a.uuid == self.state.config.action), None)
                if task
                else None
            )

            if not action or action.tool_name == "final_answer":
                logger.info("Loop complete")
                break

            # Update task status and find next
            if task:
                task.status = "completed"
                next_task = next((t for t in self.state.tasks if t.status == "pending"), None)
                if next_task:
                    self.state.config.task = next_task.uuid
                    self.state.config.action = next_task.actions[0].uuid if next_task.actions else None
                else:
                    self.state.config.task = None
                    self.state.config.action = None

            self.state.config.step += 1

        return self.state

    # Prompt templates
    def _prompt_environment(self) -> str:
        """Environment analysis prompt."""
        return f"""You are {self.state.config.ai_name}, an AI assistant.
Analyze the current environment and context.
Environment: {self.state.config.environment}
Return JSON: {{"result": "<analysis>"}}"""

    def _prompt_personality(self) -> str:
        """Personality analysis prompt."""
        return f"""You are {self.state.config.ai_name}, an AI assistant with this personality:
{self.state.config.personality}
Analyze how your personality affects your response.
Return JSON: {{"result": "<analysis>"}}"""

    def _prompt_memory(self) -> str:
        """Memory analysis prompt."""
        memories_text = "\n".join(
            [f"- {m.name} ({m.category}): {m.content}" for m in self.state.memories]
        )
        return f"""You have the following memories:
{memories_text}
Analyze relevant memories for this context.
Return JSON: {{"result": "<analysis>"}}"""

    def _prompt_tools(self) -> str:
        """Tools analysis prompt."""
        tools_text = "\n".join(
            [f"- {t.name}: {t.description}" for t in self.state.config.tools]
        )
        return f"""You have access to these tools:
{tools_text}
Analyze which tools might be useful.
Return JSON: {{"result": "<analysis>"}}"""

    def _prompt_task(self) -> str:
        """Task planning prompt."""
        return """Create tasks to accomplish the user's request.
Return JSON: {"result": [{"name": "task_name", "description": "..."}]}"""

    def _prompt_action(self) -> str:
        """Action planning prompt."""
        return """Plan actions for the current task.
Return JSON: {"result": {"task_uuid": "...", "name": "...", "tool_name": "..."}}"""

    def _prompt_use(self) -> str:
        """Tool use prompt."""
        return """Generate the payload for the tool call.
Return JSON: {"result": {...payload...}}"""
