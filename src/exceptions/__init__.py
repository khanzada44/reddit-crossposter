"""Custom exceptions package."""

from .custom_exceptions import (
    RedditBotError,
    AuthenticationError,
    SubredditBannedError,
    CrosspostDisabledError,
    RateLimitError,
)

__all__ = [
    "RedditBotError",
    "AuthenticationError",
    "SubredditBannedError",
    "CrosspostDisabledError",
    "RateLimitError",
]