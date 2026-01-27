import os
import sys

from dotenv import load_dotenv
from loguru import logger

# GARCH Model Defaults
DEFAULT_P = 1
DEFAULT_Q = 1
DEFAULT_DIST = "skewt"


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
        enqueue=True,
    )


# MARKET (+ ASSET TYPE) CLOSING TIMES IN THEIR RESPECTIOVE TZ
# + 20m for yfinance delay
_equity_base = {
    "timezones": {
        # NYSE / NASDAQ (Close 16:00) -> 16:20
        "America/New_York": {"hour": 16, "minute": 20},
        # London LSE (Close 16:30) -> 16:50
        "Europe/London": {"hour": 16, "minute": 50},
        # Xetra / Frankfurt / Paris (Close 17:30) -> 17:50
        "Europe/Berlin": {"hour": 17, "minute": 50},
        "Europe/Paris": {"hour": 17, "minute": 50},
        "Europe/Amsterdam": {"hour": 17, "minute": 50},
    },
    # SAFE FALLBACK FOR OTHER MARKETS
    "default": {"hour": 18, "minute": 0},
}
_derivate_base = {"force_tz": "America/New_York", "default": {"hour": 17, "minute": 20}}

MARKET_CUTOFFS = {
    "EQUITY": _equity_base,
    "ETF": _equity_base,
    "INDEX": _equity_base,
    "FUTURE": _derivate_base,
    "CURRENCY": _derivate_base,
    "CRYPTOCURRENCY": {"force_tz": "UTC", "default": {"hour": 23, "minute": 59}},
}
