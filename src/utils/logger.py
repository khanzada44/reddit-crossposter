"""Logging setup with Loguru."""

import sys
from pathlib import Path
from loguru import logger

from src.config.settings import get_config


def setup_logging():
    """Configure logging."""
    config = get_config()
    
    # Remove default handler
    logger.remove()
    
    # Console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=config.logging.level,
        colorize=True,
    )
    
    # File handler
    if config.logging.file:
        log_path = Path(config.logging.file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_path,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=config.logging.level,
            rotation="10 MB",
            retention="30 days",
        )
    
    return logger


# Global logger instance
app_logger = setup_logging()