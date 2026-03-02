import streamlit as st
import plotly.express as px
import pandas as pd
import requests

from config import settings
from ui import render_sidebar


# -----------------------------
# Helpers: Feature store + API
# -----------------------------

RISK_THRESHOLDS = {"high": 0.70, "medium": 0.40}

def bucket(prob: float) -> str:
    if prob >= RISK_THRESHOLDS["high"]:
        return "High Risk"
    if prob >= RISK_THRESHOLDS["medium"]:
        return "Medium Risk"
    return "Low Risk"


@st.cache_data(ttl=600)
def load_churn_features(path="data_science/feature_store/churn_features.parquet"):
    """
    Loads churn feature store file produced by Team 1.
    If file doesn't exist yet, caller will fall back to demo values.
    """
    return pd.read_parquet(path)


@st.cache_data(ttl=600)
def risk_counts_from_sample(df: pd.DataFrame, sample_n: int = 200):
    """
    Uses only a SAMPLE of customers to call the churn API.
    This avoids calling the API for 100k customers.
    Returns counts for the sample only.
    """
    sample = df.sample(min(sample_n, len(df)), random_state=42)

    low = med = high = 0

    churn_url = settings.CHURN_API_URL.rstrip("/") + "/predict/churn"

    for _, row in sample.iterrows():
        payload = {
            "customer_id": str(row["customer_id"]),
            "features": {
                "recency": float(row.get("recency", 0)),
                "frequency": float(row.get("frequency", 0)),
                "monetary": float(row.get("monetary", 0)),
                "tenure": float(row.get("tenure", 0)),
            }
        }

        r = requests.post(churn_url, json=payload, timeout=10)
        r.raise_for_status()

        prob = float(r.json()["churn_probability"])
        risk = bucket(prob)

        if risk == "High Risk":
            high += 1
        elif risk == "Medium Risk":
            med += 1
        else:
            low += 1

    return low, med, high, len(sample)


# -----------------------------
# Page config + Sidebar
# -----------------------------

st.set_page_config(page_title="ShopFlow — Overview", layout="wide")
render_sidebar("Overview")

# -----------------------------
# Page content
# -----------------------------

st.markdown("# 🛒 ShopFlow — Overview")
st.caption("Customer overview: total customers and churn risk distribution (sample-based).")
st.divider()

# -----------------------------
# KPI section (REAL total + SAMPLE risk)
# -----------------------------

try:
    df_features = load_churn_features()
    total_customers = df_features["customer_id"].nunique()

    low, med, high, n = risk_counts_from_sample(df_features, sample_n=200)

except Exception:
    # Safe fallback until feature store & live API exist
    st.warning("Feature store or churn API not ready — showing demo values.")
    total_customers = 100000
    low, med, high, n = 120, 50, 30, 200

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Customers", total_customers)
c2.metric(f"🟢 Low Risk (sample n={n})", low)
c3.metric(f"🟡 Medium Risk (sample n={n})", med)
c4.metric(f"🔴 High Risk (sample n={n})", high)

st.divider()

# -----------------------------
# Charts + Lists
# -----------------------------

left, right = st.columns([1.2, 1])

# Donut chart uses the SAME numbers as KPI
risk_df = pd.DataFrame(
    {"Risk": ["Low Risk", "Medium Risk", "High Risk"],
     "Count": [low, med, high]}
)

fig = px.pie(
    risk_df,
    names="Risk",
    values="Count",
    hole=0.55,
    title="Churn Risk Distribution (Sample)",
)
fig.update_layout(
    margin=dict(l=10, r=10, t=50, b=10),
    legend_title_text="",
)

with left:
    st.plotly_chart(fig, use_container_width=True)

# Trending products (still demo, later can be driven from rec_features.parquet)
with right:
    st.markdown("## 🔥 Trending Products (Demo)")
    trending = [
        ("Running Shoes", "Sports", "£89.99"),
        ("Wireless Earbuds", "Electronics", "£39.99"),
        ("Face Cream", "Beauty", "£22.50"),
        ("Premium Coffee Beans", "Grocery", "£14.99"),
    ]
    for name, category, price in trending:
        st.markdown(f"**{name}** — `{category}` · {price}")

st.caption("Note: Risk distribution is computed from a sampled subset to keep the dashboard fast.")