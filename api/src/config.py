import os
import sys
from datetime import date
from typing import Literal

from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel
from typing import Any


# ---Pydantic models---
DistType = Literal["normal", "t", "skewt", "ged"]


class GarchParams(BaseModel):
    p: int
    q: int
    dist: DistType


class PredictionResponse(BaseModel):
    symbol: str
    target_date: date
    model: str
    model_params: GarchParams
    predicted_volatility: float


# /report
class ReportResponse(BaseModel):
    metrics_date: list[dict[str, Any]]
    metrics_ticker: list[dict[str, Any]]
    worst_tickers: list[dict[str, Any]]


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
