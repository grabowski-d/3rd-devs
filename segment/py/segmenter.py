"""Text segmentation."""
from typing import List
class Segmenter:
    @staticmethod
    def segment_by_sentences(text: str) -> List[str]:
        return [s.strip() for s in text.split('.') if s.strip()]
    @staticmethod
    def segment_by_paragraphs(text: str) -> List[str]:
        return [p.strip() for p in text.split('\n\n') if p.strip()]
