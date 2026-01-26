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



# Complete Close price cut-offs
# + 15m for yfinance delay
MARKET_CUTOFFS = {
    'EQUITY': {
        'timezone': 'America/New_York',
        'hour': 16,
        'minute': 20
    },
    'ETF': {
        'timezone': 'America/New_York',
        'hour': 16,
        'minute': 20
    },
    'INDEX': {
        'timezone': 'America/New_York',
        'hour': 16,
        'minute': 20
    },
    'FUTURE': {
        'timezone': 'America/New_York',
        'hour': 17,
        'minute': 20
    },
    'CURRENCY': {
        'timezone': 'America/New_York',
        'hour': 17,
        'minute': 20
    },
    'CRYPTOCURRENCY': {
        'timezone': 'UTC',
        'hour': 23,
        'minute': 59
    }
}
