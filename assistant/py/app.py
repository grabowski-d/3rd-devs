"""Example application using AssistantService with thinking-planning-action loop."""

import asyncio
import json
from datetime import datetime

from .service import AssistantService
from .types import (
    Action,
    Config,
    Memory,
    MessageParam,
    State,
    Task,
    Thoughts,
    Tool,
)


async def main():
    """Run example assistant application."""

    # Initialize service
    assistant = AssistantService()

    # Define tool handlers
    def memory_handler(payload: dict) -> dict:
        """Handle memory lookup."""
        return {"status": "success", "data": f"Found memory for: {payload.get('query')}"}

    def spotify_handler(payload: dict) -> dict:
        """Handle Spotify playback."""
        return {
            "status": "success",
            "data": f"Now playing: {payload.get('play', 'unknown')}",
        }

    def final_answer_handler(payload: dict) -> dict:
        """Handle final answer."""
        return {"status": "success", "data": payload.get("answer", "")}

    # Register handlers
    assistant.register_tool_handler("memory", memory_handler)
    assistant.register_tool_handler("spotify", spotify_handler)
    assistant.register_tool_handler("final_answer", final_answer_handler)

    # Initialize state
    memory_categories = [
        {
            "name": "profiles",
            "description": "Profiles of people you know",
        },
        {
            "name": "resources",
            "description": "Learning materials and references",
        },
        {"name": "tasks", "description": "User tasks"},
        {"name": "events", "description": "Events and meetings"},
    ]

    tools: list[Tool] = [
        {
            "name": "spotify",
            "description": "Use this to play music",
            "instruction": 'Write {"play": "<song name>"}',
        },
        {
            "name": "google",
            "description": "Use this to search the web",
            "instruction": 'Write {"search": "<query>"}',
        },
        {
            "name": "memory",
            "description": "Use this to search your memory",
            "instruction": 'Write {"memory": "<memory name>"}',
        },
        {
            "name": "final_answer",
            "description": "Use this to answer the user",
            "instruction": 'Write {"answer": "<answer>"}',
        },
    ]

    config: Config = {
        "max_steps": 10,
        "step": 0,
        "task": None,
        "action": None,
        "ai_name": "Alice",
        "username": "Adam",
        "environment": "Krakow, Poland. Sunny. 20°C. At home.",
        "personality": "Friendly, curious, and helpful AI assistant.",
        "memory_categories": memory_categories,
        "tools": tools,
    }

    thoughts: Thoughts = {
        "environment": "",
        "personality": "",
        "memory": "",
        "tools": "",
    }

    memories: list[Memory] = [
        {
            "name": "Favorite songs",
            "category": "profiles",
            "content": "AC/DC — Back in Black, Queen — Bohemian Rhapsody",
        },
        {
            "name": "Learning goals",
            "category": "tasks",
            "content": "Complete AI development course",
        },
    ]

    state: State = {
        "config": config,
        "thoughts": thoughts,
        "tasks": [],
        "documents": [],
        "memories": memories,
        "tools": tools,
        "messages": [],
    }

    # Execute the loop
    user_message = "Play my favorite music"
    print(f"\n{'='*60}")
    print(f"User Message: {user_message}")
    print(f"{'='*60}")

    state = await assistant.execute_loop(state, user_message)

    # Print final state
    print("\n=== Final State ===")
    print(json.dumps(
        {
            "ai_name": state["config"]["ai_name"],
            "username": state["config"]["username"],
            "messages_count": len(state["messages"]),
            "tasks_completed": sum(
                1 for t in state["tasks"] if t["status"] == "completed"
            ),
            "memories_recalled": len(state["memories"]),
        },
        indent=2,
    ))


if __name__ == "__main__":
    asyncio.run(main())
