import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from finfetcher import DataFetcher
from loguru import logger
from numpy import log as nplog

from app.config import (
    DEFAULT_DIST,
    DEFAULT_P,
    DEFAULT_Q,
    DistType,
    GarchParams,
    PredictionResponse,
    setup_logging,
)
from app.services.database import create_preds_table, get_error_data, store_preds
from app.services.garch_model import get_garch_pred
from app.services.report import get_metrics_data, get_plots

setup_logging()

api = FastAPI(title="Financial Volatility Forecaster")
templates = Jinja2Templates(directory="app/templates")


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


@api.get("/report", response_class=HTMLResponse)
def show_report_dashboard(request: Request):
    error_data = get_error_data()

    if error_data is None or error_data.empty:
        return templates.TemplateResponse(
            "db_error.html", {"request": request}, status_code=503
        )

    error_data["error_rel"] = error_data["error_rel"] * 100

    try:
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

    except Exception as e:
        logger.exception(f"Critical error while processing report data: {e}")
        return templates.TemplateResponse(
            "processing_error.html",
            {"request": request},
            status_code=500,
        )


@api.get("/health", status_code=200)
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("app.main:api", host="0.0.0.0", port=8000, reload=True)
