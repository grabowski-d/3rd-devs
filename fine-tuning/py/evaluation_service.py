"""Evaluation service for fine-tuned models."""
from typing import List, Dict, Any, Optional
from .openai_service import OpenAIService
from .types import EvaluationMetrics


class EvaluationService:
    """Evaluate fine-tuned models."""
    
    def __init__(self):
        self.openai_service = OpenAIService()
    
    async def test_model(self, model_id: str, test_cases: List[str]) -> List[Dict[str, Any]]:
        """Test model on test cases.
        
        Args:
            model_id: Fine-tuned model ID.
            test_cases: Test queries.
        
        Returns:
            List of results.
        """
        results = []
        
        for test_input in test_cases:
            try:
                response = await self.openai_service.test_model(model_id, test_input)
                results.append({
                    'input': test_input,
                    'output': response,
                    'status': 'success'
                })
            except Exception as e:
                results.append({
                    'input': test_input,
                    'output': None,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    @staticmethod
    def compare_outputs(
        baseline_outputs: List[str],
        model_outputs: List[str]
    ) -> Dict[str, Any]:
        """Compare outputs between models.
        
        Args:
            baseline_outputs: Baseline model outputs.
            model_outputs: Fine-tuned model outputs.
        
        Returns:
            Comparison metrics.
        """
        from difflib import SequenceMatcher
        
        total = len(baseline_outputs)
        similarities = []
        
        for baseline, model in zip(baseline_outputs, model_outputs):
            similarity = SequenceMatcher(None, baseline, model).ratio()
            similarities.append(similarity)
        
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0
        
        return {
            'total_samples': total,
            'average_similarity': avg_similarity,
            'similarities': similarities
        }
    
    @staticmethod
    async def calculate_metrics(
        predictions: List[str],
        references: List[str]
    ) -> EvaluationMetrics:
        """Calculate evaluation metrics.
        
        Args:
            predictions: Model predictions.
            references: Reference outputs.
        
        Returns:
            Evaluation metrics.
        """
        # Calculate basic metrics
        correct = sum(1 for p, r in zip(predictions, references) if p == r)
        accuracy = correct / len(predictions) if predictions else 0
        
        # Simplified metrics (would need more sophisticated calculation in production)
        precision = accuracy
        recall = accuracy
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return EvaluationMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            loss=1.0 - accuracy,
            perplexity=2.0 ** (1.0 - accuracy)  # Simplified
        )
