import streamlit as st
import sqlite3
import pandas as pd
import time

st.set_page_config(page_title="UPI Fraud Analytics", layout="wide")

DB_PATH = "fraud_audit.db"

@st.cache_data(ttl=5)
def load_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql(
            "SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 50",
            conn
        )
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


st.title("🛡️ UPI Fraud Analytics Dashboard")

df = load_data()

col1, col2, col3 = st.columns(3)

col1.metric("Total Transactions", len(df))
col2.metric("Fraud Transactions", len(df[df["decision"] == "BLOCK"]) if not df.empty else 0)
col3.metric(
    "Fraud Rate (%)",
    round((len(df[df["decision"] == "BLOCK"]) / len(df)) * 100, 2)
    if len(df) > 0 else 0
)

st.divider()

st.subheader("📄 Recent Transactions")

if df.empty:
    st.info("No transactions found yet. Send transactions from Swagger.")
else:
    st.dataframe(df, use_container_width=True)

st.caption("Dashboard auto-refreshes every 5 seconds")
time.sleep(5)
st.rerun()

