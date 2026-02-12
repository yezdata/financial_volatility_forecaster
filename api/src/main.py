from pandas.errors import EmptyDataError
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from finfetcher import DataFetcher
from loguru import logger
from numpy import log as nplog

from src.config import (
    DEFAULT_DIST,
    DEFAULT_P,
    DEFAULT_Q,
    DistType,
    GarchParams,
    PredictionResponse,
    ReportResponse,
    setup_logging,
)
from src.services.database import create_preds_table, get_error_data, store_preds
from src.services.garch_model import get_garch_pred
from src.services.report import get_metrics_data

setup_logging()

api = FastAPI(title="Financial Volatility Forecaster")


# ---Endpoints---
@api.on_event("startup")
def startup_db():
    try:
        create_preds_table()
    except Exception:
        logger.exception("DB error while creating table 'garch_preds'")


@api.get("/")
def read_root():
    return RedirectResponse(url="/docs")


@api.get("/predict/{symbol}", response_model=PredictionResponse)
def predict(
    symbol: str, p: int = DEFAULT_P, q: int = DEFAULT_Q, dist: DistType = DEFAULT_DIST
):
    garch_params = GarchParams(p=p, q=q, dist=dist)
    n_params = garch_params.p + garch_params.q + 2
    model = None

    fetcher = DataFetcher(symbol)

    try:
        data = fetcher.get_data()
        target_date = fetcher.target_date

        logger.info(
            f"Got data from FinFetcher, rows: {data.count()}, target_date: {target_date}"
        )

    except Exception as e:
        logger.exception("Error while getting data from FinFetcher")
        raise HTTPException(status_code=500, detail=e)

    if data is None or target_date is None:
        raise HTTPException(
            status_code=404, detail=f"Data for symbol '{symbol}' not found"
        )

    log_returns = nplog((data["Close"] / data["Close"].shift(1)).dropna()) * 100

    if len(log_returns) < n_params * 50:
        raise HTTPException(
            status_code=500,
            detail=f"Not enough data points for GARCH({garch_params.p},{garch_params.q}) inference"
            f"Required: {n_params * 50}, Available: {len(log_returns)}",
        )

    garch_pred = get_garch_pred(log_returns, params=garch_params)
    model = "garch"
    if garch_pred is None:
        raise HTTPException(
            status_code=500,
            detail=f"GARCH model failed to converge for {symbol} (check logs)",
        )

    try:
        store_preds(
            ticker=symbol, pred=garch_pred, target_date=target_date, params=garch_params
        )
    except Exception:
        logger.exception(f"DB error while storing {symbol} predictions")

    return {
        "symbol": fetcher.symbol,
        "target_date": target_date,
        "model": model,
        "model_params": garch_params,
        "predicted_volatility": garch_pred,
    }


@api.get("/report", response_model=ReportResponse)
def get_report_data():
    try:
        error_data = get_error_data()
    except EmptyDataError:
        raise HTTPException(
            status_code=501, detail="Retrieved error data is None or empty"
        )
    except Exception:
        raise HTTPException(status_code=501, detail="Connection to DB failed")

    error_data["error_rel"] = error_data["error_rel"] * 100

    try:
        metrics_df_date, metrics_df_ticker, worst_df_tickers = get_metrics_data(
            error_data
        )

        return {
            "metrics_date": metrics_df_date.to_dict(orient="records"),
            "metrics_ticker": metrics_df_ticker.to_dict(orient="records"),
            "worst_tickers": worst_df_tickers.to_dict(orient="records"),
        }

    except Exception as e:
        logger.exception(f"Critical error while processing report data: {e}")
        raise HTTPException(status_code=500, detail="PROCESSING_ERROR")


@api.get("/health", status_code=200)
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("src.main:api", host="0.0.0.0", port=8000, reload=True)
