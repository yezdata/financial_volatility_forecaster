import os
import sys
from datetime import datetime, timedelta

import numpy as np
import yfinance as yf  # type: ignore
from loguru import logger
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DB_URL", None)

if DB_URL:
    try:
        engine = create_engine(DB_URL)
    except Exception:
        logger.error(
            "Failed to initialize DB engine. Check credentials and connectivity."
        )
        sys.exit(1)
else:
    logger.error("Environment variable DB_URL is missing.")
    sys.exit(1)


def create_perf_table() -> None:
    sql_create = text("""
        CREATE TABLE IF NOT EXISTS "garch_performance" (
        "prediction_id" integer PRIMARY KEY,
        
        "evaluation_date" date NOT NULL,
        
        "realized_vol" double precision,
        "error_raw" double precision,
        "error_abs" double precision,
        "error_rel" double precision,
        "error_sq" double precision,

        CONSTRAINT "fk_garch_performance_prediction" 
            FOREIGN KEY ("prediction_id") 
            REFERENCES "garch_preds"("id") 
            ON DELETE CASCADE
        );
    """)
    with engine.begin() as conn:
        conn.execute(sql_create)
        logger.info("Succesfully created table 'garch_performance' or table exists")


def get_missing_preds() -> dict:
    sql_extract = text("""
        SELECT 
            p.id,
            p.ticker, 
            p.target_date, 
            p.prediction
        FROM garch_preds AS p
        LEFT JOIN garch_performance AS gp
            ON p.id = gp.prediction_id
        WHERE gp.prediction_id IS NULL
            AND p.target_date < CURRENT_DATE
            AND p.target_date >= CURRENT_DATE - INTERVAL '7 days'
        ORDER BY p.target_date ASC;
    """)

    with engine.connect() as conn:
        missing_preds = conn.execute(sql_extract).fetchall()
        if not missing_preds:
            logger.info("No pending evaluations found. Everything is up to date.")
            sys.exit(0)

    logger.info(f"Found {len(missing_preds)} pending evaluations.")

    missing_preds_by_date = {}
    for row in missing_preds:
        d = row.target_date
        if d not in missing_preds_by_date:
            missing_preds_by_date[d] = []
        missing_preds_by_date[d].append(row)

    return missing_preds_by_date


def run_evaluation() -> None:
    create_perf_table()

    preds_by_date = get_missing_preds()

    for eval_date, rows in preds_by_date.items():
        tickers_list = [r.ticker for r in rows]
        logger.info(f"Processing {eval_date}: {len(tickers_list)} tickers...")

        try:
            df_bulk = yf.download(
                tickers_list,
                start=eval_date - timedelta(days=1),
                end=eval_date + timedelta(days=1),
                interval="5m",
                group_by="ticker",
                auto_adjust=True,
                progress=False,
                threads=False,
            )

            if df_bulk is None or df_bulk.empty:
                logger.warning(f"No data found for {eval_date} (Holiday?). Skipping.")
                continue

            results_to_insert = []

            for row in rows:
                try:
                    if len(tickers_list) > 1:
                        if row.ticker not in df_bulk.columns.get_level_values(0):
                            logger.warning(f"Ticker {row.ticker} missing in bulk data.")
                            continue
                        ticker_df = df_bulk[row.ticker].copy()

                    else:
                        # if df doesnt have multiindex
                        ticker_df = df_bulk.copy()

                    log_returns = (
                        np.log(
                            ticker_df["Close"] / ticker_df["Close"].shift(1).dropna()
                        )
                        * 100
                    )
                    if log_returns is None or log_returns.size == 0:
                        continue

                    real_var = np.sum(log_returns**2)
                    real_vol = np.sqrt(real_var)

                    real_vol = (
                        real_vol.item()
                        if hasattr(real_vol, "item")
                        else float(real_vol)
                    )

                    error_raw = real_vol - row.prediction
                    error_abs = abs(error_raw)
                    error_rel = (error_abs / real_vol) if real_vol != 0 else 0.0
                    error_sq = error_abs**2

                    results_to_insert.append(
                        {
                            "prediction_id": row.id,
                            "evaluation_date": datetime.now().date(),
                            "realized_vol": real_vol,
                            "error_raw": error_raw,
                            "error_abs": error_abs,
                            "error_rel": error_rel,
                            "error_sq": error_sq,
                        }
                    )

                except Exception as e:
                    logger.warning(f"Error calculating RV for {row.ticker}: {e}")
                    continue

            if results_to_insert:
                sql_insert = text("""
                    INSERT INTO garch_performance
                    (prediction_id, evaluation_date, realized_vol, error_raw, error_abs, error_rel, error_sq)
                    VALUES
                    (:prediction_id, :evaluation_date, :realized_vol, :error_raw, :error_abs, :error_rel, :error_sq)
                """)

                with engine.begin() as conn:
                    conn.execute(sql_insert, results_to_insert)

                logger.success(
                    f"Saved {len(results_to_insert)} results for {eval_date}."
                )

        except Exception as e:
            logger.error(f"Critical error processing batch for {eval_date}: {e}")


if __name__ == "__main__":
    run_evaluation()
