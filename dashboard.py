import streamlit as st
import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "fraud_audit.db")

st.set_page_config(page_title="UPI Fraud Analytics Dashboard", layout="wide")
st.title("🛡️ UPI Fraud Analytics Dashboard")

@st.cache_data(ttl=5)
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM audit_logs ORDER BY timestamp DESC", conn)
    conn.close()
    return df

df = load_data()

st.metric("Total Transactions", len(df))
st.metric("Fraud Transactions", len(df[df["decision"] == "BLOCK"]))

st.subheader("Recent Transactions")

if df.empty:
    st.warning("No transactions yet. Send from Swagger.")
else:
    st.dataframe(df, use_container_width=True)

st.caption("Auto-refresh every 5 seconds")


