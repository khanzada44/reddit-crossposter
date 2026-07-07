"""Main crossposting logic."""

import time
from datetime import datetime
from typing import List, Optional, Dict, Any

from config.settings import get_config
from src.core.reddit_client import RedditClient
from src.services.flair_service import FlairService
from src.services.ban_service import BanService
from src.services.database_service import DatabaseService
from src.utils.logger import app_logger
from src.exceptions.custom_exceptions import (
    SubredditBannedError,
    CrosspostDisabledError,
    RateLimitError,
)


class Crossposter:
    """Handle crossposting logic."""
    
    def __init__(self):
        self.logger = app_logger.bind(component="Crossposter")
        self.reddit_client = RedditClient()
        self.flair_service = FlairService(self.reddit_client)
        self.ban_service = BanService(self.reddit_client)
        self.db_service = DatabaseService()
        
        self.stats = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "banned": 0,
            "disabled": 0,
        }
    
    def crosspost_submission(self, submission, target_subreddit: str) -> Dict[str, Any]:
        """Crosspost a single submission."""
        
        self.stats["total"] += 1
        result = {
            "submission_id": submission.id,
            "target": target_subreddit,
            "success": False,
            "status": "failed",
            "error": None,
            "crosspost_url": None,
        }
        
        try:
            # Check if user is banned
            if self.ban_service.is_user_banned(target_subreddit):
                self.stats["banned"] += 1
                result["status"] = "banned"
                result["error"] = "User is banned"
                self.logger.warning(f"Banned from r/{target_subreddit}")
                return result
            
            # Check if submission already tracked
            if self.db_service.is_submission_tracked(submission.id):
                self.logger.info(f"Submission {submission.id} already tracked")
                result["status"] = "already_tracked"
                return result
            
            # Get random flair
            flair = self.flair_service.get_random_flair(target_subreddit)
            flair_id = flair.id if flair else None
            
            # Save submission to database
            submission_data = {
                "reddit_id": submission.id,
                "title": submission.title,
                "url": submission.url,
                "author": str(submission.author) if submission.author else None,
                "subreddit": str(submission.subreddit),
                "created_utc": datetime.fromtimestamp(submission.created_utc),
                "is_crossposted": True,
            }
            db_submission = self.db_service.save_submission(submission_data)
            
            if not db_submission:
                self.logger.error("Failed to save submission to database")
            
            # Perform crosspost
            crossposted = self.reddit_client.crosspost(
                submission=submission,
                target_subreddit=target_subreddit,
                flair_id=flair_id,
            )
            
            # Save crosspost record
            crosspost_data = {
                "submission_id": db_submission.id if db_submission else None,
                "target_subreddit": target_subreddit,
                "crosspost_reddit_id": crossposted.id,
                "crosspost_url": crossposted.url,
                "flair_used": flair.text if flair else None,
                "status": "success",
            }
            self.db_service.save_crosspost(crosspost_data)
            
            # Update subreddit stats
            self.db_service.update_subreddit_stats(target_subreddit, success=True)
            
            self.stats["successful"] += 1
            result["success"] = True
            result["status"] = "success"
            result["crosspost_url"] = crossposted.url
            
            self.logger.info(f"Successfully crossposted to r/{target_subreddit}")
            
        except SubredditBannedError as e:
            self.stats["banned"] += 1
            result["status"] = "banned"
            result["error"] = str(e)
            self.db_service.update_subreddit_stats(target_subreddit, success=False, banned=True)
            self.logger.warning(f"{e}")
            
        except CrosspostDisabledError as e:
            self.stats["disabled"] += 1
            result["status"] = "disabled"
            result["error"] = str(e)
            self.db_service.update_subreddit_stats(target_subreddit, success=False)
            self.logger.warning(f"{e}")
            
        except RateLimitError as e:
            result["status"] = "rate_limit"
            result["error"] = str(e)
            self.logger.error(f"Rate limit hit: {e}")
            raise  # Re-raise to handle at higher level
            
        except Exception as e:
            self.stats["failed"] += 1
            result["status"] = "error"
            result["error"] = str(e)
            self.db_service.update_subreddit_stats(target_subreddit, success=False)
            self.logger.error(f"Error: {e}")
        
        return result
    
    def run(self):
        """Main execution loop."""
        
        config = get_config()
        
        self.logger.info("=" * 70)
        self.logger.info(f"Reddit Crosspost Bot Started")
        self.logger.info(f"Source: r/{config.bot.source_subreddit}")
        self.logger.info(f"Targets: {', '.join(config.bot.target_subreddits)}")
        self.logger.info("=" * 70)
        
        # Get submissions from source
        submissions = self.reddit_client.get_submissions(
            subreddit_name=config.bot.source_subreddit,
            limit=config.bot.post_limit,
        )
        
        if not submissions:
            self.logger.info("No submissions found")
            return
        
        self.logger.info(f"Found {len(submissions)} submissions")
        
        # Process each submission
        for submission in submissions:
            self.logger.info(f"\nProcessing: {submission.title[:50]}...")
            
            # Crosspost to each target
            for target in config.bot.target_subreddits:
                try:
                    result = self.crosspost_submission(submission, target)
                    
                    # Show result
                    if result["success"]:
                        self.logger.info(f"r/{target}: Success")
                    else:
                        self.logger.info(f"r/{target}: {result['status']} - {result.get('error', '')}")
                    
                    # Wait between crossposts
                    if config.bot.delay_between_posts > 0:
                        time.sleep(config.bot.delay_between_posts)
                        
                except RateLimitError:
                    self.logger.warning("Rate limit hit, waiting 2 minutes...")
                    time.sleep(120)
                    continue
                except Exception as e:
                    self.logger.error(f"Unexpected error for r/{target}: {e}")
                    continue
            
            # Wait before next submission
            if config.bot.delay_between_posts > 0:
                time.sleep(config.bot.delay_between_posts * 2)
        
        # Show final statistics
        self._show_stats()
    
    def _show_stats(self):
        """Display statistics."""
        self.logger.info("\n" + "=" * 70)
        self.logger.info("Final Statistics:")
        self.logger.info(f"Total Attempts: {self.stats['total']}")
        self.logger.info(f"Successful: {self.stats['successful']}")
        self.logger.info(f"Failed: {self.stats['failed']}")
        self.logger.info(f"Banned: {self.stats['banned']}")
        self.logger.info(f"Disabled: {self.stats['disabled']}")
        
        # Show database stats
        all_stats = self.db_service.get_all_stats()
        if all_stats:
            self.logger.info("\n Subreddit Statistics:")
            for stats in all_stats:
                self.logger.info(
                    f"  r/{stats.subreddit_name}: "
                    f"{stats.successful_crossposts}/{stats.total_crossposts} successful"
                )
        
        self.logger.info("=" * 70)