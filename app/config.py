import os
import sys
from datetime import date
from typing import Literal

from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel

# ---Pydantic models---
DistType = Literal["normal", "t", "skewt", "ged"]


class GarchParams(BaseModel):
    p: int
    q: int
    dist: DistType


class PredictionResponse(BaseModel):
    ticker: str
    target_date: date
    model: str
    model_params: GarchParams
    predicted_volatility: float


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
