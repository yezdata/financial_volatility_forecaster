import os

import requests
import streamlit as st
from dotenv import load_dotenv
from services.dashboard import render_dashboard
from services.errors import render_db_error, render_error, render_processing_error

load_dotenv()
API_URL = os.getenv("API_URL")


def main():
    st.set_page_config(
        page_title="Financial Volatility Forecaster Report",
        page_icon="📈",
        layout="wide",
    )

    try:
        with st.spinner("Fetching data from Financial Volatility Forecaster API..."):
            response = requests.get(f"{API_URL}/report", timeout=10)

        if response.status_code == 200:
            render_dashboard(response.json())

        elif response.status_code == 501:
            render_db_error()

        elif response.status_code == 500:
            render_processing_error()

        else:
            render_error(response.status_code)

    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the Financial Volatility Forecaster API.")


if __name__ == "__main__":
    main()
