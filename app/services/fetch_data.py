from datetime import datetime, timedelta, date
import pytz
import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import BusinessDay
import numpy as np
from loguru import logger

from app.config import MARKET_CUTOFFS


# Fetching during market hours return last seen price as Close -> Need to check and remove if neccessary
def get_complete_close(df: pd.DataFrame, asset_type: str, last_day_df: date) -> pd.DataFrame:
        conf = MARKET_CUTOFFS.get(asset_type)
        if not conf:
            return df

        tz = pytz.timezone(conf['timezone'])
        now_in_tz = datetime.now(tz)
        today_in_tz = now_in_tz.date()

        cutoff_time = now_in_tz.replace(
            hour=conf['hour'], 
            minute=conf['minute'], 
            second=0, 
            microsecond=0
        )

        if (last_day_df == today_in_tz) and (now_in_tz < cutoff_time):
            df = df.iloc[:-1]
            logger.debug(f"Removed unfinished last day {last_day_df} from train data\nNow in timezone:{now_in_tz.time().strftime('%H:%M')}")

        return df



def get_data(ticker: str) -> tuple[pd.Series | None, date | None]:
    try:
        ticker_obj = yf.Ticker(ticker)
        try:
            quote_type = ticker_obj.fast_info.get('quoteType')
        except Exception:
            # Fallback pro starší verze nebo pokud fast_info selže
            quote_type = ticker_obj.info.get('quoteType')
        logger.debug(f"Detected asset type for {ticker}: {quote_type}")

        df = yf.download(ticker, period="4y", interval="1d", auto_adjust=True, progress=False)
        if df is None or df.empty:
            logger.error(f"Ticker {ticker} hasn't been found or doesn't returned any data")
            return None, None

        if isinstance(df.columns, pd.MultiIndex):
           df.columns = df.columns.droplevel(1)

        last_df_date = df.index[-1].date()

        data = get_complete_close(df, quote_type, last_df_date)


        last_data_date = data.index[-1].date()

        if quote_type == "CRYPTOCURRENCY":
            target_date = (last_data_date + timedelta(days=1))
        else:
            target_date = (last_data_date + BusinessDay(1)).date()
        
        logger.debug(data.tail())
        logger.debug(f"Final training range: {data.index.min().date()} -> {last_data_date}")
        logger.debug(f"Forecasting for target date: {target_date}")


        log_return = 100 * np.log(data['Close'] / data['Close'].shift(1)).dropna()

        logger.info(f"Fetched {ticker} data from yfinance")
        return log_return, target_date

    except Exception:
        logger.exception(f"Failed to fetch data for {ticker}")
        return None, None
        


if __name__ == "__main__":
    data, target_date = get_data("RKLB")
    if data is not None:
        logger.success(f"Test fetch successful: {data.tail()}, target_date: {target_date}")
    else:
        logger.error("Test fetch failed")
