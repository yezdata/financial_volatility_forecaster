import streamlit as st


def render_db_error():
    st.error("🔌 Database Connection Error")
    st.info("The database is currently unavailable. Please try again in a few minutes.")
    st.info(
        "**Error Context:** Could not fetch raw data from `PostreSQL` remote Database."
    )
    if st.button("Retry"):
        st.rerun()


def render_processing_error():
    st.error("❌ Report Generation Failed")
    st.info("System encountered an error while processing the retrieved data.")
    st.info(
        "**Error Context:** Raw data was successfully fetched, but the system failed during `metrics calculation` or `plot generation.`"
    )
    if st.button("Retry"):
        st.rerun()


def render_error(status_code):
    st.error("❌ Unexpected Error While Reporting Data")
    st.info("System encountered an unexpected error while fetching or processing data.")
    st.info(f"**Error Context:** `{status_code}`")
    if st.button("Retry"):
        st.rerun()
