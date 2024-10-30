import asyncio
import logging
import sys
from logging.handlers import RotatingFileHandler

from app.core.config import settings

# Configure rotating file handler (max size 1MB, backup 3 files)
rotating_handler = RotatingFileHandler("app.log", maxBytes=1e6, backupCount=3)

# Configure the root logger
logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log message format
    handlers=[
        logging.StreamHandler(sys.stdout),  # Output logs to console
        # Add a FileHandler if you want to log to a file
        logging.FileHandler("app.log"),  # Output logs to a file
    ],
)

# Create a logger for specific parts of the app
logger = logging.getLogger(settings.app_name)


async def background_task(message: str):
    logger.info(f"Storing message '{message}'.")
    await asyncio.sleep(5)
    logger.info(f"Message '{message}' stored!")
