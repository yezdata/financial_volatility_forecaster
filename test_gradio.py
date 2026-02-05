import gradio as gr
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- Generování testovacích dat ---
def get_mock_data():
    dates = pd.date_range(start=datetime.now() - timedelta(days=7), periods=7)
    df_plot = pd.DataFrame({
        'Date': dates,
        'Actual': np.random.uniform(1.0, 2.5, 7),
        'Forecast': np.random.uniform(1.0, 2.5, 7)
    })
    metrics_df = pd.DataFrame({
        'Date': dates.strftime('%Y-%m-%d'),
        'MAE': np.random.uniform(0.1, 0.5, 7),
        'RMSE': np.random.uniform(0.2, 0.7, 7),
        'R2 Score': np.random.uniform(0.6, 0.9, 7)
    })
    worst_tickers_df = pd.DataFrame({
        'Ticker': ['AAPL', 'MSFT', 'TSLA', 'NVDA', 'AMZN'],
        'Error Rate': [0.45, 0.42, 0.39, 0.35, 0.31],
        'Volatility': [2.1, 1.8, 4.5, 3.2, 2.0]
    })
    return df_plot, metrics_df, worst_tickers_df

# --- Definice Plotly grafů ---
def create_plots(df):
    # Streamlit-like dark layout
    dark_layout = dict(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#ffffff"),
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Time Series Plot
    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(
        x=df['Date'], y=df['Actual'], 
        name="Actual", 
        line=dict(color='#5271ff', width=2)
    ))
    fig_ts.add_trace(go.Scatter(
        x=df['Date'], y=df['Forecast'], 
        name="Forecast", 
        line=dict(color='#ff4b4b', width=2)
    ))
    fig_ts.update_layout(title="Volatility Time Series", **dark_layout)

    # Scatter Plot
    fig_scatter = go.Figure()
    fig_scatter.add_trace(go.Scatter(
        x=df['Actual'], y=df['Forecast'], 
        mode='markers', 
        marker=dict(size=10, color='#ff4b4b', opacity=0.7),
        name="Data Points"
    ))
    
    min_val = min(df['Actual'].min(), df['Forecast'].min())
    max_val = max(df['Actual'].max(), df['Forecast'].max())
    fig_scatter.add_trace(go.Scatter(
        x=[min_val, max_val], y=[min_val, max_val],
        mode='lines',
        line=dict(color='rgba(255,255,255,0.1)', width=1),
        showlegend=False
    ))
    
    fig_scatter.update_layout(title="Actual vs Forecast Scatter", **dark_layout)
    return fig_ts, fig_scatter

# --- UI Layout v Gradio ---
df_plot, metrics_df, worst_tickers_df = get_mock_data()
fig_ts, fig_scatter = create_plots(df_plot)

custom_css = """
.gradio-container {background-color: #0e1117 !important}
footer {display: none !important}
"""

with gr.Blocks(title="Financial Volatility Report", css=custom_css) as demo:
    gr.HTML("""
        <div style='text-align: left; padding: 10px 0;'>
            <h1 style='font-size: 2.2em; font-weight: 600; color: white; margin-bottom: 0;'>
                📈 Nasdaq-100 Volatility Forecast Evaluation (Last Week)
            </h1>
        </div>
    """)
    
    with gr.Row():
        with gr.Column():
            gr.Plot(fig_ts, show_label=False)
        with gr.Column():
            gr.Plot(fig_scatter, show_label=False)
            
    gr.Markdown("## Metrics by Date")
    gr.Dataframe(metrics_df, interactive=False)
    
    gr.Markdown("## Worst Performing Tickers")
    gr.Dataframe(worst_tickers_df, interactive=False)

if __name__ == "__main__":
    demo.launch()