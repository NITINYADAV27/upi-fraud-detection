import streamlit as st
import requests
import pandas as pd

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
BACKEND_URL = "https://YOUR-BACKEND.onrender.com"   # 🔴 CHANGE THIS
REFRESH_SEC = 5

st.set_page_config(
    page_title="UPI Fraud Analytics Dashboard",
    layout="wide"
)

st.title("🛡️ UPI Fraud Analytics Dashboard")

# --------------------------------------------------
# DATA LOADERS
# --------------------------------------------------
@st.cache_data(ttl=REFRESH_SEC)
def load_transactions():
    res = requests.get(f"{BACKEND_URL}/api/transactions", timeout=10)
    res.raise_for_status()
    return pd.DataFrame(res.json())

@st.cache_data(ttl=REFRESH_SEC)
def load_stats():
    res = requests.get(f"{BACKEND_URL}/api/analytics/stats", timeout=10)
    res.raise_for_status()
    return res.json()

# --------------------------------------------------
# FETCH DATA
# --------------------------------------------------
try:
    df = load_transactions()
    stats = load_stats()
except Exception:
    st.error("Backend not reachable. Please check backend URL.")
    st.stop()

# --------------------------------------------------
# METRICS
# --------------------------------------------------
c1, c2, c3 = st.columns(3)

c1.metric("Total Transactions", stats["total_transactions"])
c2.metric("Fraud Transactions", stats["fraud_transactions"])
c3.metric("Fraud Rate (%)", stats["fraud_rate"])

st.divider()

# --------------------------------------------------
# CHARTS (PRODUCT-LEVEL)
# --------------------------------------------------
if not df.empty:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Fraud Decision Distribution")
        st.bar_chart(df["decision"].value_counts())

    with col2:
        st.subheader("Risk Score Distribution")
        st.bar_chart(df["risk_score"])

st.divider()

# --------------------------------------------------
# TABLE
# --------------------------------------------------
st.subheader("Recent Transactions")

if df.empty:
    st.warning("No transactions yet. Send transactions via API.")
else:
    st.dataframe(df, use_container_width=True)

st.caption(f"Auto-refresh every {REFRESH_SEC} seconds")
