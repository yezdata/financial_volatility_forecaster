# Financial Volatility Forecaster: End-to-End Quantitative API Pipeline
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](#)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white)](#)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](#)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?logo=huggingface&logoColor=black)](https://yezdata-financial-volatility-forecaster.hf.space)

> **Quick Summary:** A full-stack financial engineering tool designed to predict asset volatility, bridging the gap between raw market data and actionable risk metrics. It fits reliable **GARCH(p,q)** models to capture "volatility clustering" and stores predictions in a PostgreSQL database for historical backtesting and evaluation.

---

## 📊 Project Scope: Precision in Risk Management

This project focuses on the **statistical estimation of financial risk**. By moving beyond simple standard deviation, the system uses **GARCH (Generalized Autoregressive Conditional Heteroskedasticity)** to model how volatility changes over time. This allows traders and risk managers to anticipate periods of high market turbulence based on historical price action.

The pipeline now includes **automated daily predictions for the Nasdaq-100** and a **performance dashboard** for continuous model evaluation.

## 🏆 Key Capabilities

| Component | Feature | Technology |
| :--- | :--- | :--- |
| **Data Ingestion** | Fetching historical daily returns via custom pip package (yfinance wrapper). | [FinFetcher](https://github.com/eolybq/finfetcher) |
| **Statistical Modeling** | GARCH(p,q) fitting with customizable distributions (Skew-t, GED). | `arch-py` |
| **Persistence** | Structured storage of predictions for historical tracking. | `PostgreSQL` |
| **Dashboard** | Interactive report for Nasdaq-100 forecast evaluation. | `Streamlit`, `Plotly` |
| **API Interface** | Real-time volatility prediction endpoints. | `FastAPI` |

---

## 🚀 API Usage & Documentation
Full interactive documentation (Swagger UI) is available here:
👉 **[Live API Docs](https://yezdata-financial-volatility-forecaster.hf.space/docs)**

### Prediction Evaluation Dashboard
View the performance of Nasdaq-100 forecasts from the last few days.
👉 **[Live Performance Report](https://yezdata-financial-volatility-forecaster-report.hf.space)**

### Predict Volatility Endpoint
Get a one-business day ahead volatility forecast for a specific asset.

```http
https://yezdata-financial-volatility-forecaster.hf.space/predict/{symbol}?p={p}&q={q}&dist={dist}
```
**Parameters:**
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :---: | :--- |
| `{symbol}` | string | ✅ Yes | - | Target asset ticker symbol (e.g., `AAPL`, `BTC-USD`). |
| `{p}` | int | ❌ No | `1` | **ARCH lag order**: Sensitivity to recent short-term market shocks. |
| `{q}` | int | ❌ No | `1` | **GARCH lag order**: Long-term persistence (memory) of past volatility. |
| `{dist}` | string | ❌ No | `skewt` | **Distribution**: Error assumption to account for fat tails. Available values : **normal, t, skewt, ged** |

**Example Request**
```bash
curl -X 'GET' \
  'https://yezdata-financial-volatility-forecaster.hf.space/predict/aapl?p=1&q=1&dist=skewt' \
  -H 'accept: application/json'
```

**Example Response**
```json
{
  "symbol": "AAPL",
  "target_date": "2026-01-26",
  "model": "garch",
  "model_params": {
    "p": 1,
    "q": 1,
    "dist": "skewt"
  },
  "predicted_volatility": 1.311093876892796
}
```

---

## 🛠️ Engineering Highlights

### 1. Modernized Data Pipeline
The system uses a custom data library: [FinFetcher](https://github.com/eolybq/finfetcher):
*   **FinFetcher Library:** Leverages a custom `yfinance` wrapper (available on [PyPI](https://pypi.org/project/finfetcher/)) to retrieve clean, pre-processed historical data.
*   **Log-Returns Transformation:** Automatically converts raw closing prices into stationary log-returns, essential for statistical modeling.
*   **Resiliency:** Robust error handling for API failures and data inconsistencies.

### 2. Nasdaq-100 Daily Pipeline
The project now features a production-ready automation flow:
*   **Scheduled Predictions:** `scripts/predict_nasdaq_100.py` perform daily forecasts for all Nasdaq-100 components.
*   **Automated Evaluation:** `scripts/evaluate.py` ensures that every prediction is matched against realized volatility to calculate accuracy metrics (MAE, MAPE, RMSE).

### 3. Database & Persistence Layer
Instead of transient results, every prediction is grounded in a PostgreSQL backend:
*   **Schema Design:** Stores ticker, target date, model parameters (p, q, dist), and the predicted sigma.
*   **Evaluation:** Get predictions data from PostgreSQL DB - evaluate to inspect predictions accuracy on realized days.

### 4. Performance Dashboard (Streamlit)
A new interactive dashboard provides transparency into model performance:
*   **Time-Series Tracking:** Visualize Mean Absolute Percentage Error (MAPE) trends over the last days.
*   **Asset Performance:** Identify which tickers are most difficult to forecast with scatter plots of Mean Absolute Error (MAE).
*   **Mean Metrics Table:** Shows numerical metrics for past days in their means across the Nasdaq-100 portfolio.
*   **Worst Tickers Table:** Lists assets where the model deviated most from reality, aiding in parameter tuning.

### 5. High-Fidelity Volatility Modeling (`garch_model.py`)
Utilizes the industry-standard `arch` library to perform maximum likelihood estimation:
*   **Volatility Clustering:** Captures the phenomenon where large price changes tend to be followed by large changes.
*   **Custom Distributions:** Supports `skewt` (Skewed Student's t) to account for "fat tails" and leverage effects.

### 6. Deployment & Infrastructure
*   **FastAPI + Uvicorn:** High-performance web server.
*   **PostgreSQL:** Persistent storage for predictions and performance metrics.
*   **Dockerized:** Ensures consistent environments across local development and cloud production.
*   **HuggingFace Spaces:** Seamless hosting with GitHub Actions for CI/CD.

---

## 💻 Tech Stack
*   **Backend:** Python 3.12, FastAPI, SQLAlchemy
*   **Data Science:** Pandas, NumPy, Plotly, Arch-py
*   **Infrastructure:** PostgreSQL, Docker
*   **Deployment:** HuggingFace Spaces, GitHub Actions
*   **Logging:** Loguru

---
