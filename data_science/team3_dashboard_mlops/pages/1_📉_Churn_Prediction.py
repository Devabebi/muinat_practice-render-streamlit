from ui import render_sidebar
render_sidebar("Churn Prediction")

import requests
import streamlit as st
from config import settings

st.title("📉 Churn Prediction (API)")

CHURN_BASE = settings.CHURN_API_URL.rstrip("/")
CHURN_ENDPOINT = f"{CHURN_BASE}/predict/churn"

with st.expander("Endpoint being used"):
    st.code(CHURN_ENDPOINT)

st.write("Fill inputs → click **Predict** → see churn response.")

with st.form("churn_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        customer_id = st.text_input("customer_id", value="CUST000001")
        recency = st.number_input("recency", min_value=0.0, value=45.0, step=1.0)

    with col2:
        frequency = st.number_input("frequency", min_value=0.0, value=2.0, step=1.0)
        monetary = st.number_input("monetary", min_value=0.0, value=120.5, step=10.0)

    with col3:
        tenure = st.number_input("tenure", min_value=0.0, value=6.0, step=1.0)

    submitted = st.form_submit_button("Predict")

if submitted:
    payload = {
        "customer_id": customer_id,
        "features": {
            "recency": recency,
            "frequency": frequency,
            "monetary": monetary,
            "tenure": tenure,
        },
    }

    try:
        with st.spinner("Calling churn API..."):
            r = requests.post(CHURN_ENDPOINT, json=payload, timeout=10)

        if r.status_code == 200:
            data = r.json()

            colA, colB, colC, colD = st.columns(4)
            colA.metric("Churn Probability", data.get("churn_probability"))
            colB.metric("Prediction", data.get("churn_prediction"))
            colC.metric("Confidence", data.get("confidence"))
            colD.metric("Model Version", data.get("model_version"))

            st.caption(f"Timestamp: {data.get('timestamp')}")

            with st.expander("Raw API response"):
                st.json(data)

        elif r.status_code == 422:
            st.error("422 Validation error — check request body format.")
            st.code(r.text)
        elif r.status_code == 404:
            st.error("404 Not found — customer_id not found.")
            st.code(r.text)
        else:
            st.error(f"API error: {r.status_code}")
            st.code(r.text)

    except requests.exceptions.ConnectionError:
        st.error("Could not connect. Is the churn API server running?")
        st.info(f"Expected server at: {CHURN_ENDPOINT}")
    except requests.exceptions.Timeout:
        st.error("Request timed out.")
    except Exception as e:
        st.error(f"Unexpected error: {e}")