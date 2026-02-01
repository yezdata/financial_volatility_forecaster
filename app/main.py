import time
from datetime import date
from typing import Literal

import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from loguru import logger
from numpy import log as nplog
from pandas import DataFrame
from pydantic import BaseModel

from app.config import DEFAULT_DIST, DEFAULT_P, DEFAULT_Q, setup_logging
from app.services.database import create_preds_table, get_error_data, store_preds
from app.services.garch_model import get_garch_pred
from app.services.report import get_metrics_data, get_plots

setup_logging()

api = FastAPI(title="Financial Volatility Forecaster")
templates = Jinja2Templates(directory="app/templates")


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


@api.get("/predict/{ticker}", response_model=PredictionResponse)
def predict(
    ticker: str, p: int = DEFAULT_P, q: int = DEFAULT_Q, dist: DistType = DEFAULT_DIST
):
    model = None

    ticker = ticker.upper()
    garch_params = {"p": p, "q": q, "dist": dist}

    url = f"https://yezdata-financial-data-fetcher.hf.space/get_data/{ticker}"
    params = {"period": "4y", "interval": "1d"}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        json_data = response.json()

        data = DataFrame(json_data["data"])
        target_date = json_data["target_date"]

        logger.info(
            f"Fetched data from Financial Data Fetcher API, rows: {data.count()}"
        )

    except requests.exceptions.RequestException:
        logger.exception("HTTP error while fetching Financial Data Fetcher API")
        raise HTTPException(
            status_code=500, detail=f"Data for ticker '{ticker}' not found"
        )

    except Exception:
        logger.exception("Error while fetching Financial Data Fetcher API")
        raise HTTPException(
            status_code=500, detail=f"Data for ticker '{ticker}' not found"
        )

    if data is None or target_date is None:
        raise HTTPException(
            status_code=404, detail=f"Data for ticker '{ticker}' not found"
        )

    log_returns = nplog(data["Close"] / data["Close"].shift(1)).dropna() * 100

    garch_pred = get_garch_pred(log_returns, p=p, q=q, dist=dist)
    model = "garch"
    if garch_pred is None:
        raise HTTPException(
            status_code=500,
            detail=f"GARCH model failed to converge for {ticker} (check logs)",
        )

    try:
        store_preds(
            ticker=ticker, pred=garch_pred, target_date=target_date, params=garch_params
        )
    except Exception:
        logger.exception(f"DB error while storing {ticker} predictions")

    return {
        "ticker": ticker,
        "target_date": target_date,
        "model": model,
        "model_params": garch_params,
        "predicted_volatility": garch_pred,
    }


@api.get("/report", response_class=HTMLResponse)
def show_report_dashboard(request: Request):
    error_data = None
    i = 0
    attempts = 10

    while i < attempts:
        try:
            error_data = get_error_data()
            if error_data is None or error_data.empty:
                attempts -= 1
                logger.error(
                    f"Could not get data from 'garch_performance' DB\nAttempt:{i}\nRetrying..."
                )
                time.sleep(5)

            break

        except Exception:
            attempts -= 1
            logger.exception(
                f"Got Exception while getting data from garch_performance\nAttempt: {i}\nRetrying..."
            )
            time.sleep(5)

    if error_data is None or error_data.empty:
        logger.error(
            "Could not get data from 'garch_performance' DB\nMax attempt reached\nReturning error page"
        )
        return templates.TemplateResponse(
            "db_error.html", {"request": request}, status_code=503
        )

    metrics_date, metrics_ticker, worst_tickers = get_metrics_data(error_data)
    plots = get_plots(metrics_date, metrics_ticker)

    return templates.TemplateResponse(
        "report.html",
        {
            "request": request,
            "metrics": metrics_date.to_html(
                index=False,
                classes="table table-striped table-bordered table-hover",
                border=0,
            ),
            "worst_tickers": worst_tickers.to_html(
                index=False,
                classes="table table-striped table-bordered table-hover",
                border=0,
            ),
            "plot_scatter": plots["scatter_html"],
            "plot_ts": plots["ts_html"],
        },
    )


@api.get("/health", status_code=200)
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("app.main:api", host="0.0.0.0", port=8000, reload=True)
