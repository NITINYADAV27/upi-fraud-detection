import streamlit as st
import sqlite3
import pandas as pd

from app.core.config import DB_PATH

# -----------------------------------
# Page config
# -----------------------------------
st.set_page_config(
    page_title="UPI Fraud Analytics Dashboard",
    layout="wide"
)

st.title("🛡️ UPI Fraud Analytics Dashboard")

# -----------------------------------
# Load data safely from SAME DB
# -----------------------------------
@st.cache_data(ttl=5)
def load_data():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        df = pd.read_sql(
            "SELECT * FROM audit_logs ORDER BY timestamp DESC",
            conn
        )
        conn.close()
        return df
    except Exception as e:
        # If table/db not ready yet
        return pd.DataFrame()

# -----------------------------------
# Fetch data
# -----------------------------------
df = load_data()

# -----------------------------------
# Metrics
# -----------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Transactions", len(df))

with col2:
    if not df.empty:
        st.metric(
            "Fraud Transactions",
            len(df[df["decision"] == "BLOCK"])
        )
    else:
        st.metric("Fraud Transactions", 0)

with col3:
    if not df.empty:
        fraud_rate = (
            len(df[df["decision"] == "BLOCK"]) / len(df)
        ) * 100
        st.metric("Fraud Rate (%)", f"{fraud_rate:.2f}")
    else:
        st.metric("Fraud Rate (%)", "0.00")

st.divider()

# -----------------------------------
# Transactions Table
# -----------------------------------
st.subheader("📄 Recent Transactions")

if df.empty:
    st.info("No transactions found yet. Send a transaction from Swagger.")
else:
    st.dataframe(
        df,
        use_container_width=True,
        height=400
    )

# -----------------------------------
# Auto refresh note
# -----------------------------------
st.caption("⏱️ Dashboard auto-refreshes every 5 seconds")
