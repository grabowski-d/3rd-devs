"""Example application using audio service.

Demonstrates:
- Text-to-speech (OpenAI, ElevenLabs)
- Speech-to-text (OpenAI, Groq)
- Embeddings
"""

import asyncio
import os
import logging
from audio_service import AudioService
from openai_service import OpenAIService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Main application function."""
    # Initialize services
    audio_service = AudioService(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )
    openai_service = OpenAIService()

    # Example text
    text = "Hello! This is a test of text to speech conversion."
    logger.info(f"Input text: {text}")

    # Generate speech with OpenAI
    logger.info("\n1. Generating speech with OpenAI...")
    try:
        audio_bytes = await audio_service.text_to_speech_openai(
            text, voice="nova"
        )
        logger.info(f"Generated {len(audio_bytes)} bytes of audio")

        # Save to file for demo
        with open("/tmp/openai_speech.mp3", "wb") as f:
            f.write(audio_bytes)
        logger.info("Saved to /tmp/openai_speech.mp3")

        # Transcribe back
        logger.info("\n2. Transcribing audio...")
        transcribed = await audio_service.speech_to_text_openai(audio_bytes)
        logger.info(f"Transcribed: {transcribed}")
    except Exception as e:
        logger.error(f"Error with OpenAI: {e}")

    # Try ElevenLabs if configured
    logger.info("\n3. Trying ElevenLabs...")
    elevenlabs_audio = await audio_service.text_to_speech_elevenlabs(
        "This is ElevenLabs speech synthesis."
    )
    if elevenlabs_audio:
        logger.info(f"ElevenLabs generated {len(elevenlabs_audio)} bytes")
    else:
        logger.info("ElevenLabs not configured")

    # Create embeddings
    logger.info("\n4. Creating embeddings...")
    try:
        embedding = await openai_service.create_embedding(
            "This is a test sentence for embedding."
        )
        logger.info(f"Embedding dimension: {len(embedding)}")
    except Exception as e:
        logger.error(f"Error creating embedding: {e}")

    # Count tokens
    logger.info("\n5. Counting tokens...")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": text},
    ]
    tokens = await openai_service.count_tokens(messages)
    logger.info(f"Message tokens: {tokens}")


if __name__ == "__main__":
    asyncio.run(main())
