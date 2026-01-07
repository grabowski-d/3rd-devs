"""Service for task categorization using OpenAI completions."""
import os
from typing import List, Optional
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletion


class CompletionService:
    """Service for categorizing tasks using OpenAI API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize completion service.
        
        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)
        self.valid_categories = ['work', 'private', 'other']

    async def add_label(self, task: str) -> str:
        """Categorize a task into work, private, or other.
        
        Args:
            task: Task description to categorize.
        
        Returns:
            Category: 'work', 'private', or 'other'.
        """
        messages: List[ChatCompletionMessageParam] = [
            {
                'role': 'system',
                'content': 'You are a task categorizer. Categorize the given task as \'work\', \'private\', or \'other\'. Respond with only the category name.'
            },
            {
                'role': 'user',
                'content': task
            }
        ]

        try:
            completion = self.client.chat.completions.create(
                messages=messages,
                model='gpt-4o-mini',
                max_tokens=1,
                temperature=0,
            )

            if completion.choices[0].message.content:
                label = completion.choices[0].message.content.strip().lower()
                return label if label in self.valid_categories else 'other'
            else:
                print('Unexpected response format')
                return 'other'
        
        except Exception as error:
            print(f'Error in OpenAI completion: {error}')
            return 'other'

    async def categorize_tasks(self, tasks: List[str]) -> List[dict]:
        """Categorize multiple tasks.
        
        Args:
            tasks: List of task descriptions.
        
        Returns:
            List of dicts with 'task' and 'label' keys.
        """
        results = []
        for task in tasks:
            label = await self.add_label(task)
            results.append({
                'task': task,
                'label': label
            })
        return results

    def batch_categorize_tasks(self, tasks: List[str]) -> List[dict]:
        """Synchronous batch categorization of tasks.
        
        Args:
            tasks: List of task descriptions.
        
        Returns:
            List of dicts with 'task' and 'label' keys.
        """
        results = []
        for task in tasks:
            # Synchronous version
            messages: List[ChatCompletionMessageParam] = [
                {
                    'role': 'system',
                    'content': 'You are a task categorizer. Categorize the given task as \'work\', \'private\', or \'other\'. Respond with only the category name.'
                },
                {
                    'role': 'user',
                    'content': task
                }
            ]

            try:
                completion = self.client.chat.completions.create(
                    messages=messages,
                    model='gpt-4o-mini',
                    max_tokens=1,
                    temperature=0,
                )

                if completion.choices[0].message.content:
                    label = completion.choices[0].message.content.strip().lower()
                    label = label if label in self.valid_categories else 'other'
                else:
                    label = 'other'
            except Exception as error:
                print(f'Error categorizing task: {error}')
                label = 'other'
            
            results.append({
                'task': task,
                'label': label
            })
        
        return results
