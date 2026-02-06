import pandas as pd
from numpy import sqrt as npsq


def get_metrics(df_grouped: pd.DataFrame) -> pd.DataFrame:
    mape = df_grouped["error_rel"]
    mae = df_grouped["error_abs"]
    rmse = npsq(df_grouped["error_sq"])
    bias = df_grouped["error_raw"]

    return pd.DataFrame(
        {
            "mape": mape,
            "mae": mae,
            "rmse": rmse,
            "bias": bias,
        }
    )


def get_metrics_data(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_grouped_date = df.groupby(["target_date", "model_config"]).mean(
        numeric_only=True
    )
    df_grouped_ticker = df.groupby(["ticker", "model_config"]).mean(numeric_only=True)

    worst_tickers = (
        df_grouped_ticker.sort_values("error_abs", ascending=False)
        .head(10)
        .reset_index()
    )
    worst_tickers.rename(
        columns={
            "ticker": "Ticker",
            "model_config": "Model Config",
            "error_raw": "Avg Error (Bias)",
            "error_rel": "Avg % Error",
            "error_abs": "Avg Abs Error",
            "error_sq": "Avg Squared Error",
        },
        inplace=True,
    )

    metrics_df_date = get_metrics(df_grouped_date)
    metrics_df_ticker = get_metrics(df_grouped_ticker)

    metrics_df_date = metrics_df_date.reset_index().sort_values("target_date")
    metrics_df_date.rename(
        columns={
            "target_date": "Prediction Date",
            "model_config": "Model Config",
            "mape": "MAPE",
            "mae": "MAE",
            "rmse": "RMSE",
            "bias": "Bias (mean error)",
        },
        inplace=True,
    )
    metrics_df_ticker = metrics_df_ticker.reset_index().sort_values("ticker")
    metrics_df_ticker.rename(
        columns={
            "ticker": "Ticker",
            "model_config": "Model Config",
            "mape": "MAPE",
            "mae": "MAE",
            "rmse": "RMSE",
            "bias": "Bias (mean error)",
        },
        inplace=True,
    )

    return metrics_df_date, metrics_df_ticker, worst_tickers
