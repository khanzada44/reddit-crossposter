"""Custom exceptions for the bot."""

from typing import Optional


class RedditBotError(Exception):
    """Base exception for the bot."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class AuthenticationError(RedditBotError):
    """Authentication failed."""
    pass


class SubredditBannedError(RedditBotError):
    """User is banned from subreddit."""
    pass


class CrosspostDisabledError(RedditBotError):
    """Crossposting is disabled."""
    pass


class RateLimitError(RedditBotError):
    """Rate limit exceeded."""
    pass


class ValidationError(RedditBotError):
    """Validation failed."""
    pass