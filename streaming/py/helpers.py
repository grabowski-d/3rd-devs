"""Helper functions for streaming - Python implementation"""

def is_valid_message(message) -> bool:
    """Validate message structure."""
    return (isinstance(message, dict) and
            'role' in message and
            'content' in message and
            isinstance(message.get('content'), str))
