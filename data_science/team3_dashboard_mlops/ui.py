import streamlit as st
from config import settings

def render_sidebar(active: str = ""):
    """
    Shared sidebar for all pages.
    active: optional label for the current page.
    """
    st.sidebar.markdown("## 🛒 ShopFlow")
    st.sidebar.caption("Analytics & ML Dashboard")
    st.sidebar.divider()

    # Simple connectivity check (URLs exist)
    connected = bool(settings.CHURN_API_URL) and bool(settings.REC_API_URL)
    if connected:
        st.sidebar.success("API Connected")
    else:
        st.sidebar.error("API Not Connected")

    st.sidebar.divider()
    st.sidebar.caption("DS Team 3 · Sprint 1")

    # Optional: show what page is active
    if active:
        st.sidebar.caption(f"📍 You are on: **{active}**")