"""Flair management service."""

import random
from typing import List, Optional
from dataclasses import dataclass

from src.core.reddit_client import RedditClient
from src.utils.logger import app_logger


@dataclass
class Flair:
    """Flair data class."""
    id: str
    text: str
    css_class: str = ""


class FlairService:
    """Service for managing subreddit flairs."""
    
    def __init__(self, reddit_client: RedditClient):
        self.client = reddit_client
        self.logger = app_logger.bind(component="FlairService")
        self._cache = {}
    
    def get_flairs(self, subreddit_name: str) -> List[Flair]:
        """Get available flairs for a subreddit."""
        
        # Check cache
        if subreddit_name in self._cache:
            return self._cache[subreddit_name]
        
        try:
            subreddit = self.client.get_subreddit(subreddit_name)
            flairs = []
            
            for flair in subreddit.flair.link_templates:
                flairs.append(
                    Flair(
                        id=flair["id"],
                        text=flair["text"],
                        css_class=flair.get("css_class", ""),
                    )
                )
            
            self._cache[subreddit_name] = flairs
            self.logger.debug(f"Fetched {len(flairs)} flairs from r/{subreddit_name}")
            return flairs
            
        except Exception as e:
            self.logger.error(f"Failed to fetch flairs from r/{subreddit_name}: {e}")
            return []
    
    def get_random_flair(self, subreddit_name: str) -> Optional[Flair]:
        """Get a random flair."""
        flairs = self.get_flairs(subreddit_name)
        
        if not flairs:
            return None
        
        selected = random.choice(flairs)
        self.logger.info(f" Selected flair: {selected.text}")
        return selected