"""Main application entry point."""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.crossposter import Crossposter
from src.models.database import init_db
from src.utils.logger import app_logger
from src.config.settings import get_config


def main():
    """Main function."""
    try:
        # Initialize database
        init_db()
        app_logger.info("Database initialized")
        
        # Create and run bot
        bot = Crossposter()
        bot.run()
        
    except KeyboardInterrupt:
        app_logger.info("Bot stopped by user")
    except Exception as e:
        app_logger.error(f" Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()