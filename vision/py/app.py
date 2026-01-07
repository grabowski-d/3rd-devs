"""Demo application for image vision analysis."""
import asyncio
from pathlib import Path
from openai_service import OpenAIService
from vision_service import VisionService


async def main():
    """Run image vision analysis demo."""
    # Initialize services
    openai_service = OpenAIService()
    vision_service = VisionService(openai_service)
    
    # Find image file
    image_path = None
    for possible_path in ['lessons.png', 'lessons_optimized.png', './vision/lessons.png', './vision/lessons_optimized.png']:
        if Path(possible_path).exists():
            image_path = possible_path
            break
    
    if not image_path:
        print('Error: Could not find lessons.png or lessons_optimized.png')
        print('Please ensure the image file is in the current directory or vision/ subdirectory')
        return
    
    try:
        print(f'Analyzing image: {image_path}\n')
        
        result = await vision_service.analyze_image_from_file(
            image_path,
            'Tabulate lesson numbers with like and comment counts',
            detail='high',
            model='gpt-4o'
        )
        
        print('Analysis Result:')
        print('-' * 50)
        print(result['analysis'])
        print('-' * 50)
        print()
        
        token_info = result['token_estimate']
        print('Token Usage:')
        print(f'  Image Tokens: {token_info["image_tokens"]}')
        print(f'  Text Tokens: {token_info["text_tokens"]}')
        print('-' * 50)
        print(f'  Estimated Total: {token_info["total_estimated"]}')
        print(f'  Actual Prompt Tokens: {token_info["actual_prompt_tokens"]}')
        print('-' * 50)
        print(f'  Total Usage: {token_info["actual_total_tokens"]}')
        print()
        
        print('Image Metadata:')
        metadata = result['image_metadata']
        print(f'  Dimensions: {metadata["width"]}x{metadata["height"]}')
        print(f'  Original: {metadata["original_width"]}x{metadata["original_height"]}')
    
    except Exception as error:
        print(f'Error: {error}')


if __name__ == '__main__':
    asyncio.run(main())
