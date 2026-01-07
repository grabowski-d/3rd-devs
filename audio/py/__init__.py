"""Audio processing module with TTS, STT, embeddings.

Supports:
- OpenAI Whisper (speech-to-text)
- OpenAI TTS (text-to-speech)
- ElevenLabs (advanced TTS)
- Groq Whisper (speech-to-text)
- Text embeddings
- Token counting
"""

from .openai_service import OpenAIService
from .audio_service import AudioService

__version__ = "1.0.0"
__all__ = ["OpenAIService", "AudioService"]
