"""Subreddit database models for tracking subreddit data and statistics."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, 
    String, 
    Integer, 
    DateTime, 
    Boolean, 
    Text, 
    ForeignKey, 
    Float,
    JSON,
    Index,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from .database import Base


class Subreddit(Base):
    """Subreddit information and metadata model."""
    
    __tablename__ = "subreddits"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Subreddit basic info
    name = Column(String(100), unique=True, index=True, nullable=False)
    display_name = Column(String(100), nullable=True)
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    
    # Subreddit statistics
    subscribers = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    posts_per_day = Column(Integer, default=0)
    
    # Subreddit settings
    is_private = Column(Boolean, default=False)
    is_restricted = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    # Crossposting settings
    allow_crossposts = Column(Boolean, default=True)
    require_flair = Column(Boolean, default=False)
    available_flairs = Column(JSON, default=list)
    
    # Ban status for current user
    user_banned = Column(Boolean, default=False)
    ban_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_checked = Column(DateTime, nullable=True)
    
    # Relationships
    stats = relationship("SubredditStats", back_populates="subreddit", uselist=False)
    crossposts = relationship("SubredditCrosspost", back_populates="subreddit")
    
    # Indexes
    __table_args__ = (
        Index('idx_subreddit_name', 'name'),
        Index('idx_subreddit_allow_crossposts', 'allow_crossposts'),
        Index('idx_subreddit_user_banned', 'user_banned'),
    )
    
    def __repr__(self):
        return f"<Subreddit(id={self.id}, name={self.name}, subscribers={self.subscribers})>"
    
    def __str__(self):
        return f"r/{self.name}"
    
    @hybrid_property
    def is_active(self) -> bool:
        """Check if subreddit is active (not private/restricted/archived)."""
        return not (self.is_private or self.is_restricted or self.is_archived)
    
    @hybrid_property
    def can_crosspost(self) -> bool:
        """Check if we can crosspost to this subreddit."""
        return self.allow_crossposts and self.is_active and not self.user_banned
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "title": self.title,
            "description": self.description,
            "subscribers": self.subscribers,
            "active_users": self.active_users,
            "allow_crossposts": self.allow_crossposts,
            "user_banned": self.user_banned,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class SubredditStats(Base):
    """Subreddit statistics and performance tracking."""
    
    __tablename__ = "subreddit_stats"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to subreddit
    subreddit_id = Column(Integer, ForeignKey("subreddits.id"), unique=True, nullable=False)
    
    # Crosspost statistics
    total_crossposts_attempted = Column(Integer, default=0)
    successful_crossposts = Column(Integer, default=0)
    failed_crossposts = Column(Integer, default=0)
    banned_attempts = Column(Integer, default=0)
    disabled_attempts = Column(Integer, default=0)
    
    # Success rates
    success_rate = Column(Float, default=0.0)
    failure_rate = Column(Float, default=0.0)
    
    # Daily statistics (last 7 days)
    last_7_days_success = Column(Integer, default=0)
    last_7_days_failed = Column(Integer, default=0)
    last_7_days_total = Column(Integer, default=0)
    
    # Last activity
    last_crosspost_at = Column(DateTime, nullable=True)
    last_success_at = Column(DateTime, nullable=True)
    last_failure_at = Column(DateTime, nullable=True)
    
    # Flair usage statistics
    most_used_flair = Column(String(100), nullable=True)
    flair_usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subreddit = relationship("Subreddit", back_populates="stats")
    
    # Indexes
    __table_args__ = (
        Index('idx_stats_success_rate', 'success_rate'),
        Index('idx_stats_last_crosspost', 'last_crosspost_at'),
    )
    
    def __repr__(self):
        return f"<SubredditStats(subreddit_id={self.subreddit_id}, success_rate={self.success_rate:.2f}%)>"
    
    def update_rates(self):
        """Update success and failure rates."""
        total = self.total_crossposts_attempted
        if total > 0:
            self.success_rate = (self.successful_crossposts / total) * 100
            self.failure_rate = (self.failed_crossposts / total) * 100
        else:
            self.success_rate = 0.0
            self.failure_rate = 0.0
    
    def record_success(self, flair_used: Optional[str] = None):
        """Record a successful crosspost."""
        self.total_crossposts_attempted += 1
        self.successful_crossposts += 1
        self.last_success_at = datetime.utcnow()
        self.last_crosspost_at = datetime.utcnow()
        
        self.last_7_days_success += 1
        self.last_7_days_total += 1
        
        if flair_used:
            self.most_used_flair = flair_used
            self.flair_usage_count += 1
        
        self.update_rates()
    
    def record_failure(self, reason: str = "unknown"):
        """Record a failed crosspost."""
        self.total_crossposts_attempted += 1
        self.failed_crossposts += 1
        self.last_failure_at = datetime.utcnow()
        self.last_crosspost_at = datetime.utcnow()
        
        self.last_7_days_failed += 1
        self.last_7_days_total += 1
        
        self.update_rates()
    
    def record_banned(self):
        """Record a banned attempt."""
        self.total_crossposts_attempted += 1
        self.banned_attempts += 1
        self.failed_crossposts += 1
        self.last_failure_at = datetime.utcnow()
        
        self.update_rates()
    
    def record_disabled(self):
        """Record a disabled crosspost attempt."""
        self.total_crossposts_attempted += 1
        self.disabled_attempts += 1
        self.failed_crossposts += 1
        self.last_failure_at = datetime.utcnow()
        
        self.update_rates()
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_crossposts": self.total_crossposts_attempted,
            "successful": self.successful_crossposts,
            "failed": self.failed_crossposts,
            "banned": self.banned_attempts,
            "disabled": self.disabled_attempts,
            "success_rate": f"{self.success_rate:.2f}%",
            "failure_rate": f"{self.failure_rate:.2f}%",
            "last_crosspost": self.last_crosspost_at.isoformat() if self.last_crosspost_at else None,
            "most_used_flair": self.most_used_flair,
            "flair_usage_count": self.flair_usage_count,
        }


class SubredditCrosspost(Base):
    """Individual crosspost record for a subreddit."""
    
    __tablename__ = "crossposts"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    subreddit_id = Column(Integer, ForeignKey("subreddits.id"), nullable=False)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    
    # Crosspost details
    reddit_id = Column(String(50), unique=True, nullable=True)
    title = Column(Text, nullable=False)
    url = Column(Text, nullable=True)
    flair_used = Column(String(100), nullable=True)
    flair_id = Column(String(50), nullable=True)
    
    # Status
    status = Column(String(20), default="pending")
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    subreddit = relationship("Subreddit", back_populates="crossposts")
    submission = relationship("Submission", back_populates="crossposts")
    
    # Indexes
    __table_args__ = (
        Index('idx_crosspost_status', 'status'),
        Index('idx_crosspost_subreddit', 'subreddit_id'),
        Index('idx_crosspost_created', 'created_at'),
        UniqueConstraint('subreddit_id', 'submission_id', name='uq_subreddit_submission'),
    )
    
    def __repr__(self):
        return f"<Crosspost(id={self.id}, status={self.status}, subreddit_id={self.subreddit_id})>"
    
    def mark_success(self, reddit_id: str, url: str):
        """Mark crosspost as successful."""
        self.status = "success"
        self.reddit_id = reddit_id
        self.url = url
        self.completed_at = datetime.utcnow()
    
    def mark_failed(self, error: str):
        """Mark crosspost as failed."""
        self.status = "failed"
        self.error_message = error
        self.completed_at = datetime.utcnow()
    
    def mark_banned(self):
        """Mark crosspost as banned."""
        self.status = "banned"
        self.completed_at = datetime.utcnow()
    
    def mark_disabled(self):
        """Mark crosspost as disabled."""
        self.status = "disabled"
        self.completed_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "subreddit": self.subreddit.name if self.subreddit else None,
            "title": self.title[:50] + "..." if len(self.title) > 50 else self.title,
            "status": self.status,
            "flair": self.flair_used,
            "url": self.url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class SubredditFlair(Base):
    """Track flairs for each subreddit."""
    
    __tablename__ = "subreddit_flairs"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    subreddit_id = Column(Integer, ForeignKey("subreddits.id"), nullable=False)
    
    # Flair details
    flair_id = Column(String(50), nullable=False)
    flair_text = Column(String(100), nullable=False)
    css_class = Column(String(100), nullable=True)
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subreddit = relationship("Subreddit")
    
    # Indexes
    __table_args__ = (
        Index('idx_flair_subreddit', 'subreddit_id'),
        Index('idx_flair_text', 'flair_text'),
        UniqueConstraint('subreddit_id', 'flair_id', name='uq_subreddit_flair'),
    )
    
    def __repr__(self):
        return f"<Flair(id={self.id}, text={self.flair_text}, usage={self.usage_count})>"
    
    def record_usage(self):
        """Record a usage of this flair."""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.flair_id,
            "text": self.flair_text,
            "css_class": self.css_class,
            "usage_count": self.usage_count,
            "is_active": self.is_active,
        }