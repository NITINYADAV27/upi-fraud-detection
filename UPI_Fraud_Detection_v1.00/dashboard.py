import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ==================================================
# CONFIG
# ==================================================
BACKEND_URL = "https://upi-fraud-detection-7bot.onrender.com"

HEADERS = {
    "Content-Type": "application/json"
}

st.set_page_config(
    page_title="UPI Fraud Analytics Dashboard",
    layout="wide"
)

st.title("🛡️ UPI Fraud Analytics Dashboard")

# ==================================================
# HELPERS
# ==================================================
def safe_get(url: str):
    """
    Makes a GET call and returns JSON safely.
    Never crashes the dashboard.
    """
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code != 200:
            return None, f"{url} returned {res.status_code}"
        return res.json(), None
    except Exception as e:
        return None, str(e)


# ==================================================
# BACKEND HEALTH CHECK
# ==================================================
health, err = safe_get(f"{BACKEND_URL}/")

if health is None:
    st.error("Backend not reachable. Please check backend URL.")
    st.write(err)
    st.stop()

# ==================================================
# LOAD DATA (SAFE)
# ==================================================
txs, tx_err = safe_get(f"{BACKEND_URL}/api/transactions")
stats, stats_err = safe_get(f"{BACKEND_URL}/api/analytics/stats")
decision_split, ds_err = safe_get(f"{BACKEND_URL}/api/analytics/decision-split")
risk_dist, rd_err = safe_get(f"{BACKEND_URL}/api/analytics/risk-distribution")

# ==================================================
# WARNINGS (NON-BLOCKING)
# ==================================================
if tx_err:
    st.warning("Transactions API issue")
    st.write(tx_err)

if stats_err:
    st.warning("Stats API issue")
    st.write(stats_err)

if ds_err:
    st.warning("Decision split API issue")
    st.write(ds_err)

if rd_err:
    st.warning("Risk distribution API issue")
    st.write(rd_err)

# ==================================================
# METRICS
# ==================================================
col1, col2, col3 = st.columns(3)

total_tx = stats.get("total_transactions", 0) if stats else 0
fraud_tx = stats.get("fraud_transactions", 0) if stats else 0
fraud_rate = stats.get("fraud_rate", 0) if stats else 0

col1.metric("Total Transactions", total_tx)
col2.metric("Fraud Transactions", fraud_tx)
col3.metric("Fraud Rate (%)", fraud_rate)

st.divider()

# ==================================================
# CHARTS
# ==================================================
col4, col5 = st.columns(2)

with col4:
    st.subheader("Decision Split")
    if decision_split:
        st.bar_chart(decision_split)
    else:
        st.info("No decision data available")

with col5:
    st.subheader("Risk Score Distribution")
    if risk_dist and len(risk_dist) > 0:
        st.bar_chart(pd.Series(risk_dist).value_counts().sort_index())
    else:
        st.info("No risk data available")

st.divider()

# ==================================================
# TRANSACTIONS TABLE
# ==================================================
st.subheader("Recent Transactions")

if not txs:
    st.info("No transactions processed yet.")
else:
    df = pd.DataFrame(txs)

    # Ensure timestamp readable
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    st.dataframe(df, use_container_width=True)

st.caption(f"Last refresh: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
