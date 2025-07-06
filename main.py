#!/usr/bin/env python3
"""
Discord Minecraft Server Manager Bot
Main entry point for the application
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.bot import MinecraftBot
from config.settings import settings


def setup_logging():
    """Configure logging for the application"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format=log_format,
        handlers=[
            logging.FileHandler(settings.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )


async def main():
    """Main application entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    if not settings.DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN environment variable is required")
        sys.exit(1)
    
    bot = MinecraftBot()
    
    try:
        logger.info("Starting Discord Minecraft Server Manager Bot...")
        await bot.start(settings.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    finally:
        await bot.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
