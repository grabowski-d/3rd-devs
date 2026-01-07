"""Service for image vision analysis."""
import base64
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
from .openai_service import OpenAIService

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class VisionService:
    """Service for analyzing images using OpenAI vision capabilities."""

    def __init__(self, openai_service: OpenAIService):
        """Initialize vision service.
        
        Args:
            openai_service: OpenAI service instance.
        """
        self.openai_service = openai_service
        self.compression_level = 5
        self.image_detail = 'high'

    async def process_image(self, image_path: str) -> Tuple[str, Dict[str, int]]:
        """Process and optimize image, returning base64 and metadata.
        
        Args:
            image_path: Path to image file.
        
        Returns:
            Tuple of (base64_string, metadata_dict with width/height).
        """
        if not PIL_AVAILABLE:
            raise ImportError('PIL (Pillow) is required for image processing. Install with: pip install Pillow')
        
        try:
            # Read image
            image = Image.open(image_path)
            
            # Get original dimensions
            width, height = image.size
            
            # Resize if needed
            max_dimension = 2048
            if width > max_dimension or height > max_dimension:
                image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            
            # Convert to RGB if needed (for JPEG compatibility)
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # Save to bytes
            import io
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85, optimize=True)
            image_bytes = buffer.getvalue()
            
            # Convert to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Return base64 and metadata
            metadata = {
                'width': image.width,
                'height': image.height,
                'original_width': width,
                'original_height': height
            }
            
            return image_base64, metadata
        
        except Exception as error:
            raise ValueError(f'Image processing failed: {error}')

    async def analyze_image(
        self,
        image_base64: str,
        prompt: str,
        detail: str = 'high',
        model: str = 'gpt-4o'
    ) -> ChatCompletion:
        """Analyze image using vision capabilities.
        
        Args:
            image_base64: Base64 encoded image.
            prompt: Prompt to analyze image.
            detail: Detail level ('low' or 'high').
            model: Model to use.
        
        Returns:
            ChatCompletion response with analysis.
        """
        messages: list[ChatCompletionMessageParam] = [
            {
                'role': 'system',
                'content': 'You are a helpful assistant that can analyze images and answer questions about them.'
            },
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': f'data:image/jpeg;base64,{image_base64}',
                            'detail': detail
                        }
                    },
                    {
                        'type': 'text',
                        'text': prompt
                    }
                ]
            }
        ]

        response = await self.openai_service.completion(
            messages=messages,
            model=model,
            stream=False,
            max_tokens=1024
        )

        if not isinstance(response, ChatCompletion):
            raise ValueError('Expected ChatCompletion response')
        
        return response

    async def analyze_image_from_file(
        self,
        image_path: str,
        prompt: str,
        detail: str = 'high',
        model: str = 'gpt-4o'
    ) -> Dict[str, Any]:
        """Analyze image from file path.
        
        Args:
            image_path: Path to image file.
            prompt: Prompt to analyze image.
            detail: Detail level ('low' or 'high').
            model: Model to use.
        
        Returns:
            Dict with analysis result and token information.
        """
        # Process image
        image_base64, metadata = await self.process_image(image_path)
        
        # Calculate image token cost
        image_tokens = await self.openai_service.calculate_image_tokens(
            metadata['width'],
            metadata['height'],
            detail
        )
        
        # Create messages
        messages: list[ChatCompletionMessageParam] = [
            {
                'role': 'system',
                'content': 'You are a helpful assistant that can analyze images.'
            },
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': f'data:image/jpeg;base64,{image_base64}',
                            'detail': detail
                        }
                    },
                    {
                        'type': 'text',
                        'text': prompt
                    }
                ]
            }
        ]
        
        # Count text tokens
        text_tokens = await self.openai_service.count_tokens(messages, model)
        total_tokens = image_tokens + text_tokens
        
        # Get analysis
        response = await self.analyze_image(image_base64, prompt, detail, model)
        
        return {
            'analysis': response.choices[0].message.content,
            'image_metadata': metadata,
            'token_estimate': {
                'image_tokens': image_tokens,
                'text_tokens': text_tokens,
                'total_estimated': total_tokens,
                'actual_prompt_tokens': response.usage.prompt_tokens if response.usage else 0,
                'actual_total_tokens': response.usage.total_tokens if response.usage else 0
            }
        }
