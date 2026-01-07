"""OpenAI service for fine-tuning."""
import os
from typing import List, Optional, Dict, Any, Tuple
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam


class OpenAIService:
    """OpenAI API wrapper for fine-tuning."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI service.
        
        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key)

    async def upload_file(self, file_path: str, purpose: str = 'fine-tune') -> str:
        """Upload file for fine-tuning.
        
        Args:
            file_path: Path to JSONL file.
            purpose: Purpose of file upload.
        
        Returns:
            File ID.
        """
        try:
            with open(file_path, 'rb') as f:
                response = self.client.files.create(
                    file=f,
                    purpose=purpose
                )
            return response.id
        except Exception as error:
            raise ValueError(f'Error uploading file: {error}')

    async def create_fine_tuning_job(
        self,
        model: str,
        training_file: str,
        validation_file: Optional[str] = None,
        hyperparameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create fine-tuning job.
        
        Args:
            model: Base model name.
            training_file: Training file ID.
            validation_file: Optional validation file ID.
            hyperparameters: Optional hyperparameters.
        
        Returns:
            Job ID.
        """
        try:
            kwargs: Dict[str, Any] = {
                'model': model,
                'training_file': training_file,
            }
            
            if validation_file:
                kwargs['validation_file'] = validation_file
            
            if hyperparameters:
                kwargs['hyperparameters'] = hyperparameters
            
            response = self.client.fine_tuning.jobs.create(**kwargs)
            return response.id
        
        except Exception as error:
            raise ValueError(f'Error creating fine-tuning job: {error}')

    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get fine-tuning job status.
        
        Args:
            job_id: Job ID.
        
        Returns:
            Job status details.
        """
        try:
            job = self.client.fine_tuning.jobs.retrieve(job_id)
            return {
                'id': job.id,
                'model': job.model,
                'status': job.status,
                'created_at': str(job.created_at),
                'updated_at': str(job.updated_at) if job.updated_at else None,
                'result_files': job.result_files,
                'error': job.error.message if job.error else None
            }
        except Exception as error:
            raise ValueError(f'Error getting job status: {error}')

    async def list_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List fine-tuning jobs.
        
        Args:
            limit: Maximum number of jobs to return.
        
        Returns:
            List of job details.
        """
        try:
            jobs = self.client.fine_tuning.jobs.list(limit=limit)
            return [
                {
                    'id': job.id,
                    'model': job.model,
                    'status': job.status,
                    'created_at': str(job.created_at)
                }
                for job in jobs.data
            ]
        except Exception as error:
            raise ValueError(f'Error listing jobs: {error}')

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a fine-tuning job.
        
        Args:
            job_id: Job ID.
        
        Returns:
            Success status.
        """
        try:
            self.client.fine_tuning.jobs.cancel(job_id)
            return True
        except Exception as error:
            raise ValueError(f'Error canceling job: {error}')

    async def test_model(self, model_id: str, test_message: str) -> str:
        """Test fine-tuned model.
        
        Args:
            model_id: Fine-tuned model ID.
            test_message: Test message.
        
        Returns:
            Model response.
        """
        try:
            response = self.client.chat.completions.create(
                model=model_id,
                messages=[{'role': 'user', 'content': test_message}]
            )
            return response.choices[0].message.content or ''
        except Exception as error:
            raise ValueError(f'Error testing model: {error}')
