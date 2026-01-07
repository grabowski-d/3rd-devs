"""Example chain application.

Demonstrates:
- Selecting relevant entities
- Answering questions with context
- Multi-turn conversations
"""

import asyncio
import logging
from typing import Dict, List, Any
from chain_service import ChainService
from openai_service import OpenAIService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample database
DATABASE = [
    {"id": 1, "name": "Adam", "age": 28, "occupation": "Software Engineer", "hobby": "Rock climbing"},
    {"id": 2, "name": "Michał", "age": 35, "occupation": "Data Scientist", "hobby": "Playing guitar"},
    {"id": 3, "name": "Jakub", "age": 31, "occupation": "UX Designer", "hobby": "Photography"},
]


async def main() -> None:
    """Main application."""
    openai_service = OpenAIService()
    chain = ChainService(openai_service)
    
    questions = [
        "Who is the oldest person?",
        "Tell me about Adam's hobby",
        "What does Michał do for a living?",
        "How old is Jakub?",
    ]
    
    for question in questions:
        logger.info(f"Question: {question}")
        
        # Get person names for selection
        person_names = [p["name"] for p in DATABASE]
        
        # Select most relevant person
        selected_idx = await chain.select(
            question,
            person_names,
            system_prompt="Select the most relevant person for this question."
        )
        
        person = DATABASE[selected_idx]
        
        # Answer question with person context
        answer = await chain.answer(
            question,
            context=person,
            system_prompt=f"You are answering about {person['name']}. Use this info: {person}"
        )
        
        logger.info(f"Answer: {answer}\n")


if __name__ == "__main__":
    asyncio.run(main())
