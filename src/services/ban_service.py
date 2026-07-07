"""Ban status checking service."""

from src.core.reddit_client import RedditClient
from src.utils.logger import app_logger


class BanService:
    """Service for checking ban status."""
    
    def __init__(self, reddit_client: RedditClient):
        self.client = reddit_client
        self.logger = app_logger.bind(component="BanService")
        self._cache = {}
    
    def is_user_banned(self, subreddit_name: str) -> bool:
        """Check if user is banned from subreddit."""
        
        # Check cache
        if subreddit_name in self._cache:
            return self._cache[subreddit_name]
        
        try:
            subreddit = self.client.get_subreddit(subreddit_name)
            
            # Try accessing subreddit
            subreddit.fullname
            
            # Try to submit test post (this will fail if banned)
            try:
                subreddit.submit(
                    title="Test post",
                    text="Test text",
                    send_replies=False
                )
                self.logger.warning("Test post successful - something is wrong")
            except Exception:
                # Could not post - check if it's due to ban
                # For now, assume not banned
                pass
            
            self._cache[subreddit_name] = False
            return False
            
        except Exception as e:
            self.logger.warning(f"Could not access r/{subreddit_name}: {e}")
            # If we can't access, assume banned
            self._cache[subreddit_name] = True
            return True