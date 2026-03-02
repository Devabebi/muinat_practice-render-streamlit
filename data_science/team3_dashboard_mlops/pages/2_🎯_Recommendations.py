from ui import render_sidebar
render_sidebar("Recommendations")

import requests
import streamlit as st
from config import settings
import re

st.title("🎯 Recommendations (API)")

REC_BASE = settings.REC_API_URL.rstrip("/")
CUST_PATTERN = re.compile(r"^CUST\d{6,}$")

with st.expander("Base URL being used"):
    st.code(REC_BASE)

st.caption(f"Mode: {'MOCK' if settings.MOCK_MODE else 'LIVE'}")
st.write("Enter customer_id and n → click **Get Recommendations**.")

with st.form("rec_form"):
    col1, col2 = st.columns([2, 1])
    with col1:
        customer_id = st.text_input("customer_id", value="CUST000001")
    with col2:
        n = st.slider("n (1–20)", min_value=1, max_value=20, value=5)

    submitted = st.form_submit_button("Get Recommendations")

if submitted:
    customer_id = customer_id.strip().upper()

    if not CUST_PATTERN.match(customer_id):
        st.error("Invalid customer_id format. Use format like CUST000001.")
        st.stop()

    # ✅ MOCK fallback for Render / missing API URLs
    if settings.MOCK_MODE:
        data = {
            "customer_id": customer_id,
            "recommendations": [
                {"product_id": "P1001", "product_name": "Wireless Earbuds", "category": "Electronics", "predicted_score": 0.91},
                {"product_id": "P2004", "product_name": "Running Shoes", "category": "Footwear", "predicted_score": 0.87},
                {"product_id": "P3010", "product_name": "Coffee Beans", "category": "Grocery", "predicted_score": 0.83},
                {"product_id": "P4012", "product_name": "Water Bottle", "category": "Sports", "predicted_score": 0.79},
                {"product_id": "P5015", "product_name": "Desk Lamp", "category": "Home", "predicted_score": 0.74},
            ][:n],
            "model_version": "mock-v1",
            "timestamp": "2026-03-02T00:00:00Z",
        }

        recs = data.get("recommendations", [])
        st.caption(f"Model: {data.get('model_version')} | Timestamp: {data.get('timestamp')}")

        if recs:
            st.dataframe(recs, use_container_width=True)
        else:
            st.warning("No recommendations returned.")

        with st.expander("Raw API response (mock)"):
            st.json(data)

        st.stop()

    # ✅ LIVE mode
    endpoint = f"{REC_BASE}/recommend/{customer_id}"
    params = {"n": n}

    try:
        with st.spinner("Calling recommendations API..."):
            r = requests.get(endpoint, params=params, timeout=10)

        if r.status_code == 200:
            data = r.json()
            recs = data.get("recommendations", [])

            st.caption(f"Model: {data.get('model_version')} | Timestamp: {data.get('timestamp')}")

            if recs:
                st.dataframe(recs, use_container_width=True)
            else:
                st.warning("No recommendations returned.")

            with st.expander("Raw API response"):
                st.json(data)

        elif r.status_code == 404:
            st.error("404 Not found — customer_id not found.")
            st.code(r.text)
        elif r.status_code == 422:
            st.error("422 Validation error — n must be between 1 and 20.")
            st.code(r.text)
        else:
            st.error(f"API error: {r.status_code}")
            st.code(r.text)

    except requests.exceptions.ConnectionError:
        st.error("Could not connect. Is the recommendation API server running?")
        st.info(f"Expected server at: {endpoint}")
    except requests.exceptions.Timeout:
        st.error("Request timed out.")
    except Exception as e:
        st.error(f"Unexpected error: {e}")