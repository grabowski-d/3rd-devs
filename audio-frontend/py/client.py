"""Audio frontend client for interacting with backend services."""

import aiohttp
import io
from typing import Any, Dict, List, Optional


class AudioFrontendClient:
    """Client for audio frontend backend integration.

    Handles:
    - Audio transcription via Whisper API
    - Text-to-speech via Eleven Labs
    - Chat completions
    - Message history management
    """

    def __init__(self, backend_url: str = "http://localhost:3000"):
        """Initialize audio frontend client.

        Args:
            backend_url: Base URL of backend API. Defaults to localhost:3000.
        """
        self.backend_url = backend_url
        self.api_base = f"{backend_url}/api"

    async def _fetch_api(
        self,
        endpoint: str,
        method: str = "GET",
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Make API request to backend.

        Args:
            endpoint: API endpoint path.
            method: HTTP method. Defaults to GET.
            json_data: JSON body data.
            headers: Custom headers.
            data: Form/file data.

        Returns:
            Response as dictionary.

        Raises:
            aiohttp.ClientError: If request fails.
        """
        url = f"{self.api_base}/{endpoint}"

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                url,
                json=json_data,
                headers=headers,
                data=data,
            ) as response:
                if not response.ok:
                    text = await response.text()
                    raise aiohttp.ClientError(f"API error: {text}")
                return await response.json()

    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
    ) -> str:
        """Transcribe audio file using Whisper API.

        Args:
            audio_bytes: Audio file bytes.
            filename: Audio filename. Defaults to "audio.wav".

        Returns:
            Transcribed text.

        Raises:
            ValueError: If transcription fails.
        """
        try:
            # Create form data
            form_data = aiohttp.FormData()
            form_data.add_field("file", io.BytesIO(audio_bytes), filename=filename)
            form_data.add_field("model", "whisper-1")

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/transcribe",
                    data=form_data,
                ) as response:
                    if not response.ok:
                        raise ValueError(f"Transcription failed: {response.status}")
                    result = await response.json()
                    transcription = result.get("transcription")
                    if not transcription:
                        raise ValueError("No transcription in response")
                    print(f"Transcription received: {transcription}")
                    return transcription

        except Exception as error:
            print(f"Transcription error: {error}")
            raise

    async def speak(
        self,
        text: str,
    ) -> bytes:
        """Convert text to speech using Eleven Labs.

        Args:
            text: Text to convert to speech.

        Returns:
            Audio bytes.

        Raises:
            ValueError: If speech synthesis fails.
        """
        try:
            response = await self._fetch_api(
                "speakEleven",
                method="POST",
                json_data={"text": text},
            )

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/speakEleven",
                    json={"text": text},
                ) as resp:
                    if not resp.ok:
                        raise ValueError(f"Speech synthesis failed: {resp.status}")
                    return await resp.read()

        except Exception as error:
            print(f"Speech synthesis error: {error}")
            raise

    async def chat(
        self,
        messages: List[Dict[str, str]],
    ) -> str:
        """Send chat message and get response.

        Args:
            messages: List of message dicts with 'role' and 'content'.

        Returns:
            Assistant response text.

        Raises:
            ValueError: If chat fails.
        """
        try:
            result = await self._fetch_api(
                "chat",
                method="POST",
                json_data={"messages": messages},
                headers={"Content-Type": "application/json"},
            )

            response_text = result.get("choices", [{}])[0].get("message", {}).get("content")
            if not response_text:
                raise ValueError("No response in chat result")
            return response_text

        except Exception as error:
            print(f"Chat error: {error}")
            raise

    async def transcribe_audio_blob(
        self,
        audio_bytes: bytes,
    ) -> str:
        """Transcribe audio blob (alternative method).

        Args:
            audio_bytes: Audio file bytes.

        Returns:
            Transcribed text.

        Raises:
            ValueError: If transcription fails.
        """
        try:
            form_data = aiohttp.FormData()
            form_data.add_field("file", io.BytesIO(audio_bytes), filename="audio.wav")

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/transcribe",
                    data=form_data,
                ) as response:
                    if not response.ok:
                        raise ValueError(f"Transcription failed: {response.status}")
                    result = await response.json()
                    return result.get("transcription", "")

        except Exception as error:
            print(f"Audio blob transcription error: {error}")
            raise
