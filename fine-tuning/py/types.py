"""Type definitions for fine-tuning."""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum


class Model(str, Enum):
    """Available models for fine-tuning."""
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4_MINI = "gpt-4-mini"
    GPT_3_5_TURBO = "gpt-3.5-turbo"


@dataclass
class TrainingMessage:
    """Message for training."""
    role: str  # 'system', 'user', or 'assistant'
    content: str


@dataclass
class TrainingExample:
    """Training example with messages."""
    messages: List[TrainingMessage]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TrainingConfig:
    """Configuration for training."""
    model: str
    epochs: int = 3
    batch_size: int = 1
    learning_rate: float = 1e-4
    validation_split: float = 0.1
    weight_decay: float = 0.01


@dataclass
class FineTuningJob:
    """Fine-tuning job details."""
    job_id: str
    model: str
    status: str
    created_at: str
    updated_at: Optional[str] = None
    result_files: Optional[List[str]] = None
    error: Optional[str] = None


@dataclass
class EvaluationMetrics:
    """Evaluation metrics."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    loss: float
    perplexity: float
