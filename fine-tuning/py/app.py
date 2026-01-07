"""Demo fine-tuning application."""
import asyncio
from typing import List, Dict, Any
from training_service import TrainingService
from evaluation_service import EvaluationService
from data_preparation import DataPreparation
from types import TrainingConfig, TrainingExample


# Sample training data
TRAINING_DATA = [
    {
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': 'What is AI?'},
            {'role': 'assistant', 'content': 'AI (Artificial Intelligence) is the simulation of human intelligence by machines.'}
        ]
    },
    {
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': 'Explain machine learning.'},
            {'role': 'assistant', 'content': 'Machine learning is a subset of AI that enables systems to learn from data.'}
        ]
    },
    {
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': 'What is deep learning?'},
            {'role': 'assistant', 'content': 'Deep learning uses neural networks with multiple layers to process data.'}
        ]
    },
]


async def main():
    """Run fine-tuning demo."""
    print('Fine-tuning Demo\n')
    
    # Initialize services
    config = TrainingConfig(
        model='gpt-4-mini',
        epochs=3,
        batch_size=1,
        learning_rate=1e-4
    )
    
    training_service = TrainingService(config)
    evaluation_service = EvaluationService()
    data_prep = DataPreparation()
    
    # Prepare training examples
    print('Step 1: Preparing training data...')
    examples = [
        data_prep.create_training_example(data['messages'])
        for data in TRAINING_DATA
    ]
    print(f'Created {len(examples)} training examples\n')
    
    # Split data
    print('Step 2: Splitting data...')
    train_examples, val_examples = data_prep.split_data(examples, validation_split=0.2)
    print(f'Training: {len(train_examples)}, Validation: {len(val_examples)}\n')
    
    # Prepare and upload
    print('Step 3: Preparing and uploading files...')
    try:
        file_ids = await training_service.prepare_and_upload(
            train_examples,
            val_examples
        )
        print(f'Training file ID: {file_ids["training_file_id"]}')
        if 'validation_file_id' in file_ids:
            print(f'Validation file ID: {file_ids["validation_file_id"]}\n')
    except Exception as e:
        print(f'Error preparing files: {e}\n')
        return
    
    # Start training (commented out to avoid actual API calls)
    print('Step 4: Would start fine-tuning job')
    print('  (Requires actual OpenAI API with fine-tuning enabled)')
    print('\nTo start training, use:')
    print(f'  job_id = await training_service.start_training(')
    print(f'    "{file_ids["training_file_id"]}",'
    print(f'    "{file_ids.get("validation_file_id", "None")}"')
    print(f'  )')
    
    # List jobs
    print('\nStep 5: Listing fine-tuning jobs...')
    try:
        jobs = await training_service.list_training_jobs(limit=5)
        print(f'Found {len(jobs)} jobs')
        for job in jobs:
            print(f'  - {job["id"]}: {job["status"]}')
    except Exception as e:
        print(f'Note: {e}\n')


if __name__ == '__main__':
    asyncio.run(main())
