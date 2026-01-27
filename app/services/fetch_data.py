from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import pytz
import yfinance as yf
from loguru import logger
from pandas.tseries.offsets import BusinessDay

from app.config import MARKET_CUTOFFS


# Fetching during market hours return last seen price as Close -> Need to check and remove if neccessary
def get_complete_close(
    df: pd.DataFrame, asset_type: str, last_day_df: date, ticker_tz_name: str
) -> pd.DataFrame:
    conf = MARKET_CUTOFFS.get(asset_type)
    if not conf:
        logger.warning(
            f"Unknown asset type '{asset_type}', falling back to EQUITY rules."
        )
        conf = MARKET_CUTOFFS["EQUITY"]

    if conf.get("force_tz"):
        # KRYPTO, FOREX, FUTURES
        ticker_tz_name = conf["force_tz"]
        close_time = conf["default"]
    else:
        # EQUITY, ETF, INDEX
        conf_timezones = conf.get("timezones", {})
        if ticker_tz_name in conf_timezones:
            close_time = conf_timezones[ticker_tz_name]
            logger.debug(
                f"EQUITY TICKER: Using override close_time for {ticker_tz_name}: {close_time}"
            )
        else:
            close_time = conf.get("default")
            logger.debug(
                f"EQUITY TICKER: Using default fallback close_time for {ticker_tz_name}: {close_time}"
            )

    try:
        tz = pytz.timezone(ticker_tz_name)
    except Exception:
        logger.warning(
            f"Unknown timezone '{ticker_tz_name}', fallback to America/New_York"
        )
        tz = pytz.timezone("America/New_York")

    now_in_tz = datetime.now(tz)
    today_in_tz = now_in_tz.date()

    cutoff_time = now_in_tz.replace(
        hour=close_time["hour"], minute=close_time["minute"], second=0, microsecond=0
    )

    if (last_day_df == today_in_tz) and (now_in_tz < cutoff_time):
        df = df.iloc[:-1]
        logger.debug(
            f"Removed unfinished day {last_day_df}. "
            f"Asset: {asset_type}, TZ: {ticker_tz_name}. "
            f"Current: {now_in_tz.strftime('%H:%M')} < Cutoff: {cutoff_time.strftime('%H:%M')}"
        )

    return df


def get_data(ticker: str) -> tuple[pd.Series | None, date | None]:
    try:
        ticker_obj = yf.Ticker(ticker)
        try:
            ticker_info = ticker_obj.fast_info
            quote_type = ticker_info.get("quoteType")
            if quote_type:
                quote_type = quote_type.upper()
            ticker_tz_name = ticker_info.get("timezone")

        except Exception:
            # Fallback for older v's
            quote_type = ticker_obj.info.get("quoteType")
            # Fallback for ticker timezone
            ticker_tz_name = "America/New_York"
        logger.debug(f"Detected asset type for {ticker}: {quote_type}")
        logger.debug(f"Detected timezone for {ticker}: {ticker_tz_name}")

        df = yf.download(
            ticker, period="4y", interval="1d", auto_adjust=True, progress=False
        )
        if df is None or df.empty:
            logger.error(
                f"Ticker {ticker} hasn't been found or doesn't returned any data"
            )
            return None, None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)

        last_df_date = df.index[-1].date()

        data = get_complete_close(df, quote_type, last_df_date, ticker_tz_name)

        last_data_date = data.index[-1].date()

        if quote_type == "CRYPTOCURRENCY":
            target_date = last_data_date + timedelta(days=1)
        else:
            target_date = (last_data_date + BusinessDay(1)).date()

        logger.debug(data.tail())
        logger.debug(
            f"Final training range: {data.index.min().date()} -> {last_data_date}"
        )
        logger.debug(f"Forecasting for target date: {target_date}")

        log_return = 100 * np.log(data["Close"] / data["Close"].shift(1)).dropna()

        logger.info(f"Fetched {ticker} data from yfinance")
        return log_return, target_date

    except Exception:
        logger.exception(f"Failed to fetch data for {ticker}")
        return None, None


if __name__ == "__main__":
    data, target_date = get_data("RKLB")
    if data is not None:
        logger.success(
            f"Test fetch successful: {data.tail()}, target_date: {target_date}"
        )
    else:
        logger.error("Test fetch failed")
