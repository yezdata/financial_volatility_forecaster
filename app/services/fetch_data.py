import yfinance as yf
import pandas as pd
import numpy as np
from loguru import logger
from typing import Optional


def get_data(ticker: str) -> Optional[pd.Series]:
    try:
        df = yf.download(ticker, period="4y", interval="1d", auto_adjust=True, progress=False)

        if df is None or df.empty:
            logger.error(f"Ticker {ticker} hasn't been found or doesn't returned any data")
            return None

        if isinstance(df.columns, pd.MultiIndex):
           df.columns = df.columns.droplevel(1)

        logger.debug(df.tail())
        start_date = df.index.min().date()
        end_date = df.index.max().date()
        logger.debug(f"Training data range: {start_date} -> {end_date}")

        log_return = 100 * np.log(df['Close'] / df['Close'].shift(1)).dropna()

        logger.info(f"Fetched {ticker} data from yfinance")
        return log_return

    except Exception:
        logger.exception(f"Failed to fetch data for {ticker}")
        return None
        


if __name__ == "__main__":
    data = get_data("AAPL")
    if data is not None:
        logger.success(f"Test fetch successful: {data.tail()}")
    else:
        logger.error("Test fetch failed")
