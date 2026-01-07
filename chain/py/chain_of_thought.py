"""Chain-of-thought question answering service."""

import json
from typing import Any, Dict, List, Optional
from openai.types.chat import ChatCompletionMessageParam

from .openai_service import OpenAIService


class ChainOfThought:
    """Service for chain-of-thought question answering with person selection."""

    def __init__(self, openai_service: OpenAIService):
        """Initialize chain-of-thought service.

        Args:
            openai_service: OpenAI service instance.
        """
        self.openai_service = openai_service
        # In-memory database
        self.database: List[Dict[str, Any]] = [
            {
                "id": 1,
                "name": "Adam",
                "age": 28,
                "occupation": "Software Engineer",
                "hobby": "Rock climbing",
            },
            {
                "id": 2,
                "name": "Michał",
                "age": 35,
                "occupation": "Data Scientist",
                "hobby": "Playing guitar",
            },
            {
                "id": 3,
                "name": "Jakub",
                "age": 31,
                "occupation": "UX Designer",
                "hobby": "Photography",
            },
        ]

    async def select_person(self, question: str) -> int:
        """Select most relevant person for question.

        Args:
            question: Question to route to person.

        Returns:
            Person ID (1, 2, or 3).
        """
        messages: List[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": (
                    "You are an assistant that selects the most relevant "
                    "person for a given question. Respond with only the "
                    "person's ID (1 for Adam, 2 for Michał, or 3 for Jakub)."
                ),
            },
            {"role": "user", "content": question},
        ]

        try:
            completion = await self.openai_service.completion(
                messages=messages,
                model="gpt-4o",
                max_tokens=1,
                temperature=0,
            )

            content = completion.choices[0].message.content
            if content:
                try:
                    person_id = int(content.strip())
                    if person_id in [1, 2, 3]:
                        return person_id
                except ValueError:
                    pass
            return 1  # Default to Adam
        except Exception as error:
            print(f"Error in select_person: {error}")
            return 1

    async def answer_question(self, question: str, person_id: int) -> str:
        """Answer question about specific person.

        Args:
            question: Question to answer.
            person_id: ID of person to answer about.

        Returns:
            Answer to question.
        """
        person = next(
            (p for p in self.database if p["id"] == person_id), self.database[0]
        )

        messages: List[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": (
                    f"You are an assistant answering questions about "
                    f"{person['name']}. Use the following information: "
                    f"{json.dumps(person)}"
                ),
            },
            {"role": "user", "content": question},
        ]

        try:
            completion = await self.openai_service.completion(
                messages=messages,
                model="gpt-4o",
                max_tokens=500,
                temperature=0.7,
            )

            return (
                completion.choices[0].message.content
                or "I couldn't generate an answer."
            )
        except Exception as error:
            print(f"Error in answer_question: {error}")
            return "Sorry, I encountered an error while trying to answer the question."

    async def process_question(self, question: str) -> Dict[str, Any]:
        """Process question through chain-of-thought.

        Args:
            question: Question to process.

        Returns:
            Result with person, person_id, and answer.
        """
        # Step 1: Select person
        person_id = await self.select_person(question)
        person = next(
            (p for p in self.database if p["id"] == person_id), self.database[0]
        )

        # Step 2: Answer question
        answer = await self.answer_question(question, person_id)

        return {
            "question": question,
            "person_id": person_id,
            "person_name": person["name"],
            "answer": answer,
        }

    def get_person(self, person_id: int) -> Optional[Dict[str, Any]]:
        """Get person from database.

        Args:
            person_id: Person ID.

        Returns:
            Person record or None.
        """
        return next(
            (p for p in self.database if p["id"] == person_id), None
        )

    def get_all_people(self) -> List[Dict[str, Any]]:
        """Get all people in database.

        Returns:
            List of people.
        """
        return self.database.copy()
