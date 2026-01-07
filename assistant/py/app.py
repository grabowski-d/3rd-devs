"""Example application using Assistant service."""

import asyncio
import json
import logging
from typing import Dict, Any
from uuid import uuid4

from types import (
    State,
    Config,
    Tool,
    MemoryCategory,
    Memory,
    Thoughts,
    ActionResult,
)
from assistant_service import AssistantService
from openai_service import OpenAIService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def mock_tool_handler(tool_name: str, payload: Dict[str, Any]) -> ActionResult:
    """Mock tool handler for demonstration."""
    if tool_name == "spotify":
        return ActionResult(
            status="success",
            data=f"Now playing: {payload.get('play', 'Unknown')}" 
        )
    elif tool_name == "google":
        return ActionResult(
            status="success",
            data=f"Search results for: {payload.get('search', 'query')}"
        )
    elif tool_name == "memory":
        return ActionResult(
            status="success",
            data={
                "name": "Favorite songs",
                "category": "profiles",
                "content": "AC/DC, Queen, Led Zeppelin, Guns N' Roses, Nirvana"
            }
        )
    elif tool_name == "final_answer":
        return ActionResult(
            status="success",
            data=payload.get("answer", "No answer provided")
        )
    else:
        return ActionResult(
            status="error",
            data=f"Unknown tool: {tool_name}"
        )


async def main() -> None:
    """Main application function."""
    logger.info("Starting assistant example")

    # Memory categories
    memory_categories = [
        MemoryCategory(
            name="profiles",
            description="Profiles of people you know"
        ),
        MemoryCategory(
            name="resources",
            description="Learning materials and references"
        ),
        MemoryCategory(
            name="tasks",
            description="Tasks from the user"
        ),
        MemoryCategory(
            name="events",
            description="Past or upcoming events"
        ),
    ]

    # Available tools
    tools = [
        Tool(
            name="spotify",
            description="Use this to play music and search for songs",
            instruction='Write {"play": "<song name>"}'
        ),
        Tool(
            name="google",
            description="Use this to search the web",
            instruction='Write {"search": "<query>"}'
        ),
        Tool(
            name="memory",
            description="Use this to search your memory",
            instruction='Write {"memory": "<memory name>"}'
        ),
        Tool(
            name="final_answer",
            description="Use this to answer the user",
            instruction='Write {"answer": "<answer>"}'
        ),
    ]

    # Initial memories
    memories = [
        Memory(
            name="Favorite songs",
            category="profiles",
            content="AC/DC — Back in Black, Queen — Bohemian Rhapsody"
        ),
        Memory(
            name="Finish S05E02",
            category="tasks",
            content="Complete the lesson"
        ),
    ]

    # Create config
    config = Config(
        max_steps=10,
        step=0,
        task=None,
        action=None,
        ai_name="Alice",
        username="Adam",
        environment="Krakow, Poland. Sunny. 20°C. At home.",
        personality="You're curious and happy to chat. You love AI and music.",
        memory_categories=memory_categories,
        tools=tools,
    )

    # Create initial state
    state = State(
        config=config,
        thoughts=Thoughts(),
        memories=memories,
        tools=tools,
    )

    # Create services
    openai_service = OpenAIService()
    assistant = AssistantService(state, openai_service)

    # Register tool handlers
    for tool in tools:
        assistant.register_tool_handler(
            tool.name,
            lambda payload, t=tool.name: mock_tool_handler(t, payload)
        )

    # Execute the assistant loop
    user_message = "Play my favorite music"
    logger.info(f"User message: {user_message}")

    try:
        final_state = await assistant.execute_loop(user_message, max_steps=5)
        logger.info("Assistant loop completed")
        logger.info(f"Final state: {json.dumps(final_state.to_dict(), indent=2)}")
    except Exception as e:
        logger.error(f"Error executing assistant loop: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
