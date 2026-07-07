"""Application configuration using Pydantic Settings."""

from typing import List, Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from functools import lru_cache


class RedditConfig(BaseSettings):
    """Reddit API configuration."""
    
    client_id: str = Field(..., env="REDDIT_CLIENT_ID")
    client_secret: str = Field(..., env="REDDIT_CLIENT_SECRET")
    user_agent: str = Field("MyBot/1.0", env="REDDIT_USER_AGENT")
    username: str = Field(..., env="REDDIT_USERNAME")
    password: str = Field(..., env="REDDIT_PASSWORD")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class BotConfig(BaseSettings):
    """Bot behavior configuration."""
    
    source_subreddit: str = Field(..., env="SOURCE_SUBREDDIT")
    target_subreddits: List[str] = Field(..., env="TARGET_SUBREDDITS")
    post_limit: int = Field(10, ge=1, le=50, env="POST_LIMIT")
    delay_between_posts: int = Field(60, ge=30, env="DELAY_BETWEEN_POSTS")
    max_retries: int = Field(3, ge=1, le=5, env="MAX_RETRIES")
    
    @validator("target_subreddits", pre=True)
    def parse_subreddits(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",")]
        return v


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    
    url: str = Field("sqlite:///data/bot.db", env="DATABASE_URL")
    pool_size: int = Field(5, env="DB_POOL_SIZE")
    max_overflow: int = Field(10, env="DB_MAX_OVERFLOW")


class LoggingConfig(BaseSettings):
    """Logging configuration."""
    
    level: str = Field("INFO", env="LOG_LEVEL")
    file: str = Field("logs/bot.log", env="LOG_FILE")


class AppConfig(BaseSettings):
    """Main application configuration."""
    
    app_name: str = "RedditCrosspostBot"
    app_version: str = "1.0.0"
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(True, env="DEBUG")
    
    reddit: RedditConfig = RedditConfig()
    bot: BotConfig = BotConfig()
    database: DatabaseConfig = DatabaseConfig()
    logging: LoggingConfig = LoggingConfig()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_config() -> AppConfig:
    """Get cached configuration."""
    return AppConfig()