from datetime import date
from typing import Literal

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from loguru import logger
from pydantic import BaseModel

from app.config import DEFAULT_DIST, DEFAULT_P, DEFAULT_Q, setup_logging
from app.services.database import create_preds_table, get_error_data, store_preds
from app.services.fetch_data import get_data
from app.services.garch_model import get_garch_pred

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

    data, target_date = get_data(ticker)
    if data is None or target_date is None:
        raise HTTPException(
            status_code=404, detail=f"Data for ticker '{ticker}' not found"
        )

    garch_pred = get_garch_pred(data, p=p, q=q, dist=dist)
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
def show_report_dashboard():
    error_data = get_error_data

    metrics = get_metrics_data(error_data)
    plots = get_plots(error_data)

    return templates.TemplateResponse("report.html", {
            "request": request,
            "target_date": str(df.iloc[0]['target_date']),
            "count": len(df),
            "mape": mape,
            "mae": mae,
            "rmse": rmse,
            "bias": bias,
            "plot_scatter": plots['scatter_html'],
            "plot_hist": plots['hist_html'],
            "table_html": table_html
    })



@api.get("/health", status_code=200)
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("app.main:api", host="0.0.0.0", port=8000, reload=True)
