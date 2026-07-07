"""Reddit API client wrapper."""

import time
from typing import List, Optional
import praw
from praw.exceptions import APIException

from src.config.settings import get_config
from src.exceptions.custom_exceptions import (
    AuthenticationError,
    RateLimitError,
    RedditBotError,
    SubredditBannedError,
    CrosspostDisabledError,
)
from src.utils.logger import app_logger


class RedditClient:
    """Reddit API client with error handling."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = app_logger.bind(component="RedditClient")
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize PRAW client."""
        try:
            self.client = praw.Reddit(
                client_id=self.config.reddit.client_id,
                client_secret=self.config.reddit.client_secret,
                user_agent=self.config.reddit.user_agent,
                username=self.config.reddit.username,
                password=self.config.reddit.password,
            )
            
            # Test authentication
            self.client.user.me()
            self.logger.info("Successfully authenticated with Reddit")
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            raise AuthenticationError(f"Authentication failed: {e}")
    
    def get_subreddit(self, name: str):
        """Get subreddit object."""
        try:
            return self.client.subreddit(name)
        except Exception as e:
            self.logger.error(f"Failed to get subreddit r/{name}: {e}")
            raise RedditBotError(f"Failed to get subreddit: {e}")
    
    def get_submissions(self, subreddit_name: str, limit: int = 10) -> List:
        """Get hot submissions from subreddit."""
        try:
            subreddit = self.get_subreddit(subreddit_name)
            submissions = []
            
            for submission in subreddit.hot(limit=limit):
                submissions.append(submission)
            
            self.logger.info(f"Fetched {len(submissions)} submissions from r/{subreddit_name}")
            return submissions
            
        except Exception as e:
            self.logger.error(f"Failed to get submissions: {e}")
            return []
    
    def crosspost(self, submission, target_subreddit: str, title: str = None, flair_id: str = None):
        """Crosspost submission to target subreddit."""
        try:
            if title is None:
                title = submission.title
            
            kwargs = {
                "subreddit": target_subreddit,
                "title": title,
            }
            
            if flair_id:
                kwargs["flair_id"] = flair_id
            
            crossposted = submission.crosspost(**kwargs)
            
            self.logger.info(f"Crossposted to r/{target_subreddit}")
            return crossposted
            
        except APIException as e:
            error_str = str(e).lower()
            
            if "banned" in error_str:
                raise SubredditBannedError(f"Banned from r/{target_subreddit}")
            elif "crosspost" in error_str and "disabled" in error_str:
                raise CrosspostDisabledError(f"Crossposting disabled in r/{target_subreddit}")
            elif "rate" in error_str:
                raise RateLimitError(f"Rate limit exceeded: {e}")
            else:
                raise RedditBotError(f"API error: {e}")
                
        except Exception as e:
            self.logger.error(f"Crosspost failed: {e}")
            raise RedditBotError(f"Crosspost failed: {e}")