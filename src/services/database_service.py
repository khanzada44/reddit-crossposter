"""Database service for managing submissions and crossposts."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from src.models import Submission, Crosspost, SubredditStats, get_session
from src.utils.logger import app_logger


class DatabaseService:
    """Service for database operations."""
    
    def __init__(self):
        self.logger = app_logger.bind(component="DatabaseService")
    
    def save_submission(self, submission_data: Dict[str, Any]) -> Optional[Submission]:
        """Save or update submission in database."""
        try:
            with get_session() as session:
                # Check if exists
                existing = session.query(Submission).filter(
                    Submission.reddit_id == submission_data["reddit_id"]
                ).first()
                
                if existing:
                    # Update existing
                    for key, value in submission_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                    session.commit()
                    return existing
                else:
                    # Create new
                    submission = Submission(**submission_data)
                    session.add(submission)
                    session.commit()
                    session.refresh(submission)
                    self.logger.info(f"Saved submission: {submission.reddit_id}")
                    return submission
                    
        except Exception as e:
            self.logger.error(f"Failed to save submission: {e}")
            return None
    
    def save_crosspost(self, crosspost_data: Dict[str, Any]) -> Optional[Crosspost]:
        """Save crosspost record."""
        try:
            with get_session() as session:
                crosspost = Crosspost(**crosspost_data)
                session.add(crosspost)
                session.commit()
                session.refresh(crosspost)
                self.logger.info(f"Saved crosspost: {crosspost.id}")
                return crosspost
                
        except Exception as e:
            self.logger.error(f"Failed to save crosspost: {e}")
            return None
    
    def update_crosspost_status(self, crosspost_id: int, status: str, error_message: str = None):
        """Update crosspost status."""
        try:
            with get_session() as session:
                crosspost = session.query(Crosspost).filter(
                    Crosspost.id == crosspost_id
                ).first()
                
                if crosspost:
                    crosspost.status = status
                    if error_message:
                        crosspost.error_message = error_message
                    session.commit()
                    return True
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to update crosspost: {e}")
            return False
    
    def update_subreddit_stats(self, subreddit_name: str, success: bool, banned: bool = False):
        """Update subreddit statistics."""
        try:
            with get_session() as session:
                stats = session.query(SubredditStats).filter(
                    SubredditStats.subreddit_name == subreddit_name
                ).first()
                
                if not stats:
                    stats = SubredditStats(subreddit_name=subreddit_name)
                    session.add(stats)
                
                stats.total_crossposts += 1
                if success:
                    stats.successful_crossposts += 1
                    stats.last_crosspost_at = datetime.utcnow()
                else:
                    stats.failed_crossposts += 1
                if banned:
                    stats.banned_attempts += 1
                
                session.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to update stats: {e}")
            return False
    
    def get_submission_by_reddit_id(self, reddit_id: str) -> Optional[Submission]:
        """Get submission by Reddit ID."""
        try:
            with get_session() as session:
                return session.query(Submission).filter(
                    Submission.reddit_id == reddit_id
                ).first()
        except Exception as e:
            self.logger.error(f"Failed to get submission: {e}")
            return None
    
    def get_recent_crossposts(self, limit: int = 10) -> List[Crosspost]:
        """Get recent crossposts."""
        try:
            with get_session() as session:
                return session.query(Crosspost).order_by(
                    desc(Crosspost.created_at)
                ).limit(limit).all()
        except Exception as e:
            self.logger.error(f"Failed to get recent crossposts: {e}")
            return []
    
    def get_subreddit_stats(self, subreddit_name: str) -> Optional[SubredditStats]:
        """Get statistics for a subreddit."""
        try:
            with get_session() as session:
                return session.query(SubredditStats).filter(
                    SubredditStats.subreddit_name == subreddit_name
                ).first()
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            return None
    
    def get_all_stats(self) -> List[SubredditStats]:
        """Get all subreddit statistics."""
        try:
            with get_session() as session:
                return session.query(SubredditStats).order_by(
                    desc(SubredditStats.total_crossposts)
                ).all()
        except Exception as e:
            self.logger.error(f"Failed to get all stats: {e}")
            return []
    
    def is_submission_tracked(self, reddit_id: str) -> bool:
        """Check if submission is already tracked."""
        return self.get_submission_by_reddit_id(reddit_id) is not None