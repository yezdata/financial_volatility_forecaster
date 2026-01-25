from datetime import datetime, timezone
import pandas as pd
from pandas.tseries.offsets import BusinessDay
from sqlalchemy import create_engine, text
from loguru import logger

from app.config import DB_URL


engine = create_engine(DB_URL)


def create_table() -> None:
    sql_create = text("""
        CREATE TABLE IF NOT EXISTS garch_preds (
            id SERIAL PRIMARY KEY,
            ticker VARCHAR(10) NOT NULL,
            execution_time TIMESTAMP DEFAULT NOW(),
            target_date DATE NOT NULL,
            p INTEGER NOT NULL,
            q INTEGER NOT NULL,
            dist VARCHAR(15) NOT NULL,
            prediction FLOAT NOT NULL
        );
    """)
    with engine.begin() as conn:
        conn.execute(sql_create) 
        logger.info("Succesfully create table 'garch_preds'")




def store_pred(ticker: str, pred: float, last_data_date: pd.Timestamp, params: dict) -> None:
    target_date = (last_data_date + BusinessDay(1)).date()
    execution_time = datetime.now(timezone.utc)
    pred = pred.item() if hasattr(pred, "item") else float(pred)

    sql_insert = text("""
        INSERT INTO garch_preds (ticker, target_date, prediction, execution_time, p, q, dist)
        VALUES (:ticker, :target_date, :prediction, :execution_time, :p, :q, :dist)
    """)

    with engine.begin() as conn:
        conn.execute(sql_insert, {
            "ticker": ticker, 
            "target_date": target_date, 
            "execution_time": execution_time,
            "p": params["p"],
            "q": params["q"],
            "dist": params["dist"],
            "prediction": pred
        })
        logger.info(f"Stored prediction for {ticker} (Target: {target_date})")
