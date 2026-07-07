"""Validation utilities."""

import re
from typing import Optional


def validate_subreddit(name: str) -> bool:
    """Validate subreddit name."""
    if not name:
        return False
    
    # Subreddit names: 3-21 characters, only letters, numbers, underscores
    pattern = r'^[a-zA-Z0-9_]{3,21}$'
    return bool(re.match(pattern, name))


def validate_title(title: str, max_length: int = 300) -> bool:
    """Validate post title."""
    if not title:
        return False
    return len(title.strip()) <= max_length


def sanitize_input(text: str) -> str:
    """Sanitize user input."""
    if not text:
        return ""
    # Remove special characters
    return re.sub(r'[^\w\s\-.,!?]', '', text).strip()