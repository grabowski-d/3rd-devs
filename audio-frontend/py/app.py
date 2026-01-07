"""Example application using audio frontend client."""

import asyncio
from .client import AudioFrontendClient


async def main():
    """Run example audio frontend application."""

    # Initialize client
    client = AudioFrontendClient(backend_url="http://localhost:3000")

    print("\n" + "=" * 60)
    print("Audio Frontend Client Example")
    print("=" * 60 + "\n")

    # Example 1: Chat
    print("1. Testing chat functionality...")
    try:
        messages = [
            {"role": "user", "content": "Hello, how are you today?"},
        ]
        response = await client.chat(messages)
        print(f"   Response: {response}")
    except Exception as error:
        print(f"   Error: {error}")

    # Example 2: Transcription
    print("\n2. Testing transcription...")
    try:
        # Create sample audio bytes (would be real audio in practice)
        sample_audio = b"\x00" * 44100  # Placeholder
        result = await client.transcribe_audio_blob(sample_audio)
        print(f"   Transcription: {result}")
    except Exception as error:
        print(f"   Error (expected - no real audio): {error}")

    # Example 3: Chat with context
    print("\n3. Testing multi-turn chat...")
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is Python?"},
        ]
        response = await client.chat(messages)
        print(f"   Response: {response}")
    except Exception as error:
        print(f"   Error: {error}")

    print("\n" + "=" * 60)
    print("\nNote: This client requires a backend server running at:")
    print("  http://localhost:3000")
    print("\nMake sure the backend has these endpoints:")
    print("  - POST /api/chat")
    print("  - POST /api/transcribe")
    print("  - POST /api/speakEleven")


if __name__ == "__main__":
    asyncio.run(main())
