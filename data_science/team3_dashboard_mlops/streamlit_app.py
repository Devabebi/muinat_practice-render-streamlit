import streamlit as st
from config import settings

st.set_page_config(page_title="ShopFlow Dashboard", layout="wide")

st.title("🛒 ShopFlow Customer Intelligence Dashboard")
st.write("Use the left sidebar to switch pages.")

with st.expander("🔧 Current API Configuration"):
    st.write("CHURN_API_URL:", settings.CHURN_API_URL)
    st.write("REC_API_URL:", settings.REC_API_URL)

st.info(
    "Page 1: Churn Prediction (Team 1 contract)\n\n"
    "Page 2: Recommendations (Team 2 contract)\n\n"
    "To switch from mock → real APIs later, update only `.env`."
)