"""Summary helpers."""
def summarize_text(text: str, max_length: int = 150) -> str:
    sentences = text.split('.')
    return '.'.join(sentences[:max_length//50])+'.' if len(sentences) > 1 else text
