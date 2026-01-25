# Financial Volatility Forecaster: End-to-End Quantitative Pipeline

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/spaces/yezdata/financial-volatility-forecaster)
![yfinance](https://img.shields.io/badge/Data-yfinance-green)

> **Quick Summary:** A full-stack financial engineering tool designed to predict asset volatility, bridging the gap between raw market data and actionable risk metrics. It fetches historical data via `yfinance`, fits simple but reliable **GARCH(p,q)** models to capture "volatility clustering," and stores predictions in a PostgreSQL database for historical backtesting and evaluation.

---

## 📊 Project Scope: Precision in Risk Management

This project focuses on the **statistical estimation of financial risk**. By moving beyond simple standard deviation, the system uses **GARCH (Generalized Autoregressive Conditional Heteroskedasticity)** to model how volatility changes over time. This allows traders and risk managers to anticipate periods of high market turbulence based on historical price action.

## 🏆 Key Capabilities

| Component | Feature | Technology |
| :--- | :--- | :--- |
| **Data Ingestion** | Automated fetching of 4-year historical daily returns. | `yfinance` |
| **Econometric Modeling** | GARCH(p,q) fitting with customizable distributions (Skew-t, GED). | `arch-py` |
| **Persistence** | Structured storage of predictions for future evaluation, model drifts inspection and retraining | `PostgreSQL` |
| **API Interface** | Real-time volatility prediction endpoints. | `FastAPI` |

---

## 🚀 API Usage & Documentation
Full interactive documentation (Swagger UI) is available here:
👉 **[Live API Docs](https://yezdata-financial-volatility-forecaster.hf.space/docs)**

### Predict Volatility Endpoint
Get a one-business day ahead volatility forecast for a specific asset.

```http
https://yezdata-financial-volatility-forecaster.hf.space/predict/{ticker}?p={p}&q={q}&dist={dist}
```
**Parameters:**
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :---: | :--- |
| `{ticker}` | string | ✅ Yes | - | Target Stock Ticker symbol (e.g., `AAPL`, `BTC-USD`). |
| `{p}` | int | ❌ No | `1` | **ARCH lag order**: Sensitivity to recent short-term market shocks. |
| `{q}` | int | ❌ No | `1` | **GARCH lag order**: Long-term persistence (memory) of past volatility. |
| `{dist}` | string | ❌ No | `skewt` | **Distribution**: Error assumption to account for fat tails. Available values : **norm, t, skewt, ged** |

**Example Request**
```bash
curl -X 'GET' \
  'https://yezdata-financial-volatility-forecaster.hf.space/predict/aapl?p=1&q=1&dist=skewt' \
  -H 'accept: application/json'
```

```http
https://yezdata-financial-volatility-forecaster.hf.space/predict/aapl?p=1&q=1&dist=skewt
```

**Example Response**
```json
{
  "ticker": "AAPL",
  "garch_params": {
    "p": 1,
    "q": 1,
    "dist": "skewt"
  },
  "predicted_volatility": 1.3150833040963563
}
```

---

## 🛠️ Engineering Highlights

### 1. Robust Data Pipeline (`fetch_data.py`)
Handling financial data requires precision. The ingestion engine:
*   **Log-Returns Transformation:** Automatically converts raw closing prices into stationary log-returns, essential for statistical modeling.
*   **Auto-Cleaning:** Handles multi-index columns and missing values from the Yahoo Finance API.
*   **Resiliency:** Implements logging via `loguru` to track data gaps and fetch errors.

### 2. High-Fidelity Volatility Modeling (`garch_model.py`)
The system utilizes the industry-standard `arch` library to perform maximum likelihood estimation:
*   **Volatility Clustering:** Captures the phenomenon where large price changes tend to be followed by large changes.
*   **Custom Distributions:** Supports `skewt` (Skewed Student's t) to account for "fat tails" and leverage effects in financial markets.
*   **Forecasting:** Generates one-business day ahead conditional volatility forecasts.

### 3. Database & Persistence Layer
Instead of transient results, every prediction is grounded in a PostgreSQL backend:
*   **Schema Design:** Stores ticker, target date, model parameters (p, q, dist), and the predicted sigma.
*   **Retraining:** Get predictions data from PostgreSQL DB - evaluate to inspect any model drifts, retrain model weights, rebuild and redeploy.
*   **Business Logic:** Automatically calculates the `target_date` using `BusinessDay` offsets to ensure predictions align with market sessions.

### 4. Deployment & Infrastructure (FastAPI + Docker)
Exposed the core logic via a modern FastAPI backend, ready for containerized scaling.
*   **API Design:** Clean Pydantic models for request validation and type-safe responses.
*   **Containerization:** Fully **Dockerized**, ensuring consistent environments across local development and cloud production.
*   **Cloud Ready:** Optimized and deployed on **HuggingFace Spaces**

---

## 💻 Tech Stack
*   **Backend:** Python 3.12, FastAPI, SQLAlchemy
*   **Data Science:** Pandas, NumPy, yfinance, Arch-py
*   **Infrastructure:** PostgreSQL, Docker
*   **Deployment:** HuggingFace Spaces, GitHub Actions
*   **Logging:** Loguru

---
