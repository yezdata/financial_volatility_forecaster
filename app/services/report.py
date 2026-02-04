import pandas as pd
import plotly.express as px
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
            # TODO: model_config
        }
    )


def get_metrics_data(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_grouped_date = df.groupby("target_date").mean(numeric_only=True)
    df_grouped_ticker = df.groupby("ticker").mean(numeric_only=True)

    worst_tickers = df.sort_values("error_abs", ascending=False)[
        ["ticker", "error_raw", "error_rel", "error_sq"]
    ].head(10)
    worst_tickers.rename(
        columns={
            "ticker": "Ticker",
            "error_raw": "Error",
            "error_rel": "Percent Error",
            "error_sq": "Squared Error",
        },
        inplace=True,
    )

    metrics_df_date = get_metrics(df_grouped_date)
    metrics_df_ticker = get_metrics(df_grouped_ticker)

    metrics_df_date = metrics_df_date.reset_index().sort_values("target_date")
    metrics_df_date.rename(
        columns={
            "target_date": "Prediction Date",
            "mape": "MAPE",
            "mae": "MAE",
            "rmse": "RMSE",
            "bias": "Bias (mean error)",
            # TODO: model_config
        },
        inplace=True,
    )
    metrics_df_ticker = metrics_df_ticker.reset_index().sort_values("ticker")
    metrics_df_ticker.rename(
        columns={
            "ticker": "Ticker",
            "mape": "MAPE",
            "mae": "MAE",
            "rmse": "RMSE",
            "bias": "Bias (mean error)",
            # TODO: model_config
        },
        inplace=True,
    )

    return metrics_df_date, metrics_df_ticker, worst_tickers


def get_plots(
    metrics_df_date: pd.DataFrame, metrics_df_ticker: pd.DataFrame
) -> dict[str, str]:
    # TODO: model_config -> color
    ts_fig = px.line(
        metrics_df_date,
        x="Prediction Date",
        y="MAPE",
        title="Mean Percentage Absolute Error for Nasdaq-100",
        markers=True,
    )
    ts_fig_html = ts_fig.to_html(full_html=False, include_plotlyjs=False)

    # TODO: model_config -> color
    scatter_fig = px.scatter(
        metrics_df_ticker,
        x="Ticker",
        y="MAE",
        title="Mean Absolute Error per last week",
    )
    scatter_fig_html = scatter_fig.to_html(full_html=False, include_plotlyjs=False)

    return {"ts_html": ts_fig_html, "scatter_html": scatter_fig_html}
