"""Training service for fine-tuning."""
from typing import Optional, Dict, Any
from .openai_service import OpenAIService
from .data_preparation import DataPreparation
from .types import TrainingConfig, TrainingExample


class TrainingService:
    """Handle training workflow."""
    
    def __init__(self, config: TrainingConfig):
        """Initialize training service.
        
        Args:
            config: Training configuration.
        """
        self.openai_service = OpenAIService()
        self.data_preparation = DataPreparation()
        self.config = config
    
    async def prepare_and_upload(
        self,
        training_examples: list[TrainingExample],
        validation_examples: Optional[list[TrainingExample]] = None
    ) -> Dict[str, str]:
        """Prepare data and upload files.
        
        Args:
            training_examples: Training examples.
            validation_examples: Optional validation examples.
        
        Returns:
            Dict with training_file_id and optional validation_file_id.
        """
        # Prepare training file
        training_path = await self.data_preparation.prepare_jsonl_file(
            training_examples,
            'training_data.jsonl'
        )
        
        # Validate
        is_valid, errors = await self.data_preparation.validate_jsonl(training_path)
        if not is_valid:
            raise ValueError(f'Validation errors: {errors}')
        
        # Upload training file
        training_file_id = await self.openai_service.upload_file(training_path)
        
        result = {'training_file_id': training_file_id}
        
        # Prepare and upload validation file if provided
        if validation_examples:
            validation_path = await self.data_preparation.prepare_jsonl_file(
                validation_examples,
                'validation_data.jsonl'
            )
            
            is_valid, errors = await self.data_preparation.validate_jsonl(validation_path)
            if not is_valid:
                raise ValueError(f'Validation errors: {errors}')
            
            validation_file_id = await self.openai_service.upload_file(validation_path)
            result['validation_file_id'] = validation_file_id
        
        return result
    
    async def start_training(
        self,
        training_file_id: str,
        validation_file_id: Optional[str] = None
    ) -> str:
        """Start fine-tuning job.
        
        Args:
            training_file_id: Uploaded training file ID.
            validation_file_id: Optional validation file ID.
        
        Returns:
            Job ID.
        """
        hyperparameters = {
            'n_epochs': self.config.epochs,
            'batch_size': self.config.batch_size,
            'learning_rate_multiplier': self.config.learning_rate,
            'weight_decay': self.config.weight_decay
        }
        
        job_id = await self.openai_service.create_fine_tuning_job(
            model=self.config.model,
            training_file=training_file_id,
            validation_file=validation_file_id,
            hyperparameters=hyperparameters
        )
        
        return job_id
    
    async def check_progress(self, job_id: str) -> Dict[str, Any]:
        """Check training progress.
        
        Args:
            job_id: Job ID.
        
        Returns:
            Job status.
        """
        return await self.openai_service.get_job_status(job_id)
    
    async def list_training_jobs(self, limit: int = 10) -> list[Dict[str, Any]]:
        """List all training jobs.
        
        Args:
            limit: Max jobs to return.
        
        Returns:
            List of jobs.
        """
        return await self.openai_service.list_jobs(limit)
    
    async def cancel_training(self, job_id: str) -> bool:
        """Cancel training job.
        
        Args:
            job_id: Job ID.
        
        Returns:
            Success status.
        """
        return await self.openai_service.cancel_job(job_id)
