import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- Konfigurace stránky ---
st.set_page_config(
    page_title="Financial Volatility Report",
    page_icon="📈",
    layout="wide"
)

# --- Generování testovacích dat (Nahraďte vaší logikou) ---
def get_mock_data():
    dates = pd.date_range(start=datetime.now() - timedelta(days=7), periods=7)
    
    # Data pro grafy
    df_plot = pd.DataFrame({
        'Date': dates,
        'Actual': np.random.uniform(1.0, 2.5, 7),
        'Forecast': np.random.uniform(1.0, 2.5, 7)
    })
    
    # Tabulka metrik
    metrics_df = pd.DataFrame({
        'Date': dates.strftime('%Y-%m-%d'),
        'MAE': np.random.uniform(0.1, 0.5, 7),
        'RMSE': np.random.uniform(0.2, 0.7, 7),
        'R2 Score': np.random.uniform(0.6, 0.9, 7)
    })
    
    # Nejhorší tickery
    worst_tickers_df = pd.DataFrame({
        'Ticker': ['AAPL', 'MSFT', 'TSLA', 'NVDA', 'AMZN'],
        'Error Rate': [0.45, 0.42, 0.39, 0.35, 0.31],
        'Volatility': [2.1, 1.8, 4.5, 3.2, 2.0]
    })
    
    return df_plot, metrics_df, worst_tickers_df

df_plot, metrics_df, worst_tickers_df = get_mock_data()

# --- Definice Plotly grafů ---
def create_plots(df):
    # Time Series Plot
    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(x=df['Date'], y=df['Actual'], name="Actual"))
    fig_ts.add_trace(go.Scatter(x=df['Date'], y=df['Forecast'], name="Forecast"))
    fig_ts.update_layout(title="Volatility Time Series", template="plotly_white")

    # Scatter Plot
    fig_scatter = go.Figure()
    fig_scatter.add_trace(go.Scatter(
        x=df['Actual'], y=df['Forecast'], 
        mode='markers', 
        marker=dict(size=10, color='rgba(152, 0, 0, .8)')
    ))
    fig_scatter.update_layout(title="Actual vs Forecast Scatter", template="plotly_white")
    
    return fig_ts, fig_scatter

fig_ts, fig_scatter = create_plots(df_plot)

# --- UI Layout (Ekvivalent vašeho HTML) ---
st.markdown("<h1 style='text-align: center;'>📈 Nasdaq-100 Volatility Forecast Evaluation (Last Week)</h1>", unsafe_allow_html=True)

# Sekce grafů (2 sloupce)
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_ts, use_container_width=True)

with col2:
    st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# Tabulka metrik
st.header("Metrics by Date")
st.dataframe(metrics_df, use_container_width=True, hide_index=True)

st.divider()

# Tabulka nejhorších tickerů
st.header("Worst Performing Tickers")
st.table(worst_tickers_df) # st.table je statická, st.dataframe je interaktivní
