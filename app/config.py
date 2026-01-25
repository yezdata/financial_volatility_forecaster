from dotenv import load_dotenv
from loguru import logger
import sys
import os


# GARCH Model Defaults
DEFAULT_P = 1
DEFAULT_Q = 1
DEFAULT_DIST = 'skewt'


# ENV VARIABLES
load_dotenv()
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
DB_URL = os.getenv("DB_URL")


# LOGGING
def setup_logging() -> None:
    logger.remove()
    logger.add(
        sys.stdout, 
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=LOG_LEVEL,
        enqueue=True
    )
