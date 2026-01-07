"""Data preparation for fine-tuning."""
import json
from typing import List, Dict, Any, Tuple
from pathlib import Path
from .types import TrainingExample, TrainingMessage


class DataPreparation:
    """Prepare data for fine-tuning."""
    
    @staticmethod
    def create_training_example(
        messages: List[Dict[str, str]],
        metadata: Dict[str, Any] = None
    ) -> TrainingExample:
        """Create training example from messages.
        
        Args:
            messages: List of message dicts with 'role' and 'content'.
            metadata: Optional metadata.
        
        Returns:
            TrainingExample.
        """
        training_messages = [
            TrainingMessage(role=msg['role'], content=msg['content'])
            for msg in messages
        ]
        return TrainingExample(messages=training_messages, metadata=metadata)
    
    @staticmethod
    async def prepare_jsonl_file(
        examples: List[TrainingExample],
        output_path: str
    ) -> str:
        """Prepare JSONL file for training.
        
        Args:
            examples: Training examples.
            output_path: Output file path.
        
        Returns:
            Path to created file.
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            for example in examples:
                line = {
                    'messages': [
                        {'role': msg.role, 'content': msg.content}
                        for msg in example.messages
                    ]
                }
                if example.metadata:
                    line['metadata'] = example.metadata
                
                f.write(json.dumps(line) + '\n')
        
        return str(output_file)
    
    @staticmethod
    def split_data(examples: List[TrainingExample], validation_split: float = 0.1) -> Tuple[List[TrainingExample], List[TrainingExample]]:
        """Split data into training and validation sets.
        
        Args:
            examples: All examples.
            validation_split: Fraction for validation (0-1).
        
        Returns:
            Tuple of (training_examples, validation_examples).
        """
        split_idx = int(len(examples) * (1 - validation_split))
        return examples[:split_idx], examples[split_idx:]
    
    @staticmethod
    async def validate_jsonl(file_path: str) -> Tuple[bool, List[str]]:
        """Validate JSONL file format.
        
        Args:
            file_path: Path to JSONL file.
        
        Returns:
            Tuple of (is_valid, error_messages).
        """
        errors = []
        
        try:
            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                    
                    try:
                        data = json.loads(line)
                        
                        # Check required fields
                        if 'messages' not in data:
                            errors.append(f'Line {line_num}: Missing "messages" field')
                            continue
                        
                        # Validate messages
                        messages = data['messages']
                        if not isinstance(messages, list) or len(messages) < 1:
                            errors.append(f'Line {line_num}: "messages" must be non-empty list')
                            continue
                        
                        # Check message structure
                        for msg_idx, msg in enumerate(messages):
                            if 'role' not in msg or 'content' not in msg:
                                errors.append(f'Line {line_num}, message {msg_idx}: Missing "role" or "content"')
                            
                            if msg['role'] not in ['system', 'user', 'assistant']:
                                errors.append(f'Line {line_num}: Invalid role "{msg["role"]}"')
                    
                    except json.JSONDecodeError as e:
                        errors.append(f'Line {line_num}: Invalid JSON - {str(e)}')
        
        except Exception as e:
            errors.append(f'File read error: {str(e)}')
        
        return len(errors) == 0, errors
