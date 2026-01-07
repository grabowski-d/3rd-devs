"""Helper functions for streaming service."""
from typing import Any, Dict


def is_valid_message(message: Any) -> bool:
    """Validate chat message format.
    
    Args:
        message: Message to validate.
    
    Returns:
        True if message has 'role' and 'content' (string) keys.
    """
    return (
        isinstance(message, dict) and
        'role' in message and
        'content' in message and
        isinstance(message['content'], str)
    )


def validate_messages(messages: Any) -> bool:
    """Validate list of chat messages.
    
    Args:
        messages: Messages to validate.
    
    Returns:
        True if valid.
    """
    return (
        isinstance(messages, list) and
        len(messages) > 0 and
        all(is_valid_message(msg) for msg in messages)
    )
