import streamlit as st
import pandas as pd
import plotly.express as px


def render_dashboard(data):

    metrics_date = pd.DataFrame(data["metrics_date"])
    metrics_ticker = pd.DataFrame(data["metrics_ticker"])
    worst_tickers = pd.DataFrame(data["worst_tickers"])

    fig_mape_ts = px.line(
        metrics_date,
        x="Prediction Date",
        y="MAPE",
        color="Model Config",
        title="Mean Percentage Absolute Error for Nasdaq-100",
        markers=True,
    )

    fig_scatter = px.scatter(
        metrics_ticker,
        x="Ticker",
        y="MAE",
        color="Model Config",
        title="Mean Absolute Error per last 10 days",
    )

    # UI
    st.markdown(
        "<h1 style='text-align: center;'>📈 Nasdaq-100 Volatility Forecast Evaluation (Last 10 Market Days)</h1>",
        unsafe_allow_html=True,
    )

    # Plots
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_mape_ts, width="stretch")

    with col2:
        st.plotly_chart(fig_scatter, width="stretch")

    st.divider()

    # Tables
    st.header("Metrics by Date")
    st.dataframe(metrics_date, width="stretch", hide_index=True)

    st.divider()

    st.header("Worst Performing Tickers")
    st.dataframe(worst_tickers, width="stretch", hide_index=True)
    # st.table(worst_tickers)
