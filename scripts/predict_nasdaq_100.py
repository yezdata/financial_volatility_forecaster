import os
import sys
from concurrent.futures import ThreadPoolExecutor
from io import StringIO

import pandas as pd
import requests
from loguru import logger

API_URL = os.getenv("API_URL")
if not API_URL:
    logger.error("API_URL environment variable is not set.")
    sys.exit(1)


def get_nasdaq_100() -> list | None:
    url = "https://en.wikipedia.org/wiki/Nasdaq-100"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        tables = pd.read_html(StringIO(response.text))

        nasdaq_table = next(t for t in tables if "Ticker" in t.columns)

        tickers = nasdaq_table["Ticker"].tolist()
        logger.info(f"Found {len(tickers)} tickers.")
        return tickers

    except Exception:
        logger.exception("Error with getting Nasdaq-100 from Wikipedia")
        return None


API_ENDPOINT = API_URL + "/predict/{ticker}"


def trigger_ticker(ticker: str) -> tuple[bool, str, str | None]:
    params = {"p": 4, "q": 4, "dist": "skewt"}
    try:
        response = requests.get(
            API_ENDPOINT.format(ticker=ticker), params=params, timeout=15
        )
        response.raise_for_status()
        return True, ticker, None
    except Exception as e:
        return False, ticker, str(e)


def main():
    tickers = get_nasdaq_100()
    if not tickers:
        sys.exit(1)
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_ticker = {executor.submit(trigger_ticker, t): t for t in tickers}

        for future in future_to_ticker:
            success, ticker, error = future.result()

            if not success:
                logger.error(f"ERROR {ticker}: {error}")

    logger.info("Succesfully finished predicting Nasdaq-100")


if __name__ == "__main__":
    main()
