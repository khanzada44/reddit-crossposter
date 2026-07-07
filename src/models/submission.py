"""Submission database model."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Submission(Base):
    """Tracked submission model."""
    
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    reddit_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(Text, nullable=False)
    url = Column(Text, nullable=True)
    author = Column(String(100), nullable=True)
    subreddit = Column(String(100), nullable=False)
    created_utc = Column(DateTime, nullable=False)
    is_crossposted = Column(Boolean, default=False)
    crosspost_count = Column(Integer, default=0)
    last_crossposted = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    crossposts = relationship("Crosspost", back_populates="original_submission")
    
    def __repr__(self):
        return f"<Submission(id={self.id}, reddit_id={self.reddit_id}, title={self.title[:30]})>"


class Crosspost(Base):
    """Crosspost record model."""
    
    __tablename__ = "crossposts"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    target_subreddit = Column(String(100), nullable=False)
    crosspost_reddit_id = Column(String(50), unique=True, nullable=True)
    crosspost_url = Column(Text, nullable=True)
    flair_used = Column(String(100), nullable=True)
    status = Column(String(20), default="pending")  # pending, success, failed, banned, disabled
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    original_submission = relationship("Submission", back_populates="crossposts")
    
    def __repr__(self):
        return f"<Crosspost(id={self.id}, target={self.target_subreddit}, status={self.status})>"


class SubredditStats(Base):
    """Subreddit statistics model."""
    
    __tablename__ = "subreddit_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    subreddit_name = Column(String(100), unique=True, index=True, nullable=False)
    total_crossposts = Column(Integer, default=0)
    successful_crossposts = Column(Integer, default=0)
    failed_crossposts = Column(Integer, default=0)
    banned_attempts = Column(Integer, default=0)
    last_crosspost_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SubredditStats(name={self.subreddit_name}, total={self.total_crossposts})>"