import streamlit as st
import sqlite3
import pandas as pd
import time

# ---------------- CONFIG ----------------
DB_PATH = "fraud_audit.db"
REFRESH_SECONDS = 5
PAGE_SIZE = 50

st.set_page_config(
    page_title="UPI Fraud Analytics",
    layout="wide"
)

# ---------------- DB UTILS ----------------
@st.cache_data(ttl=REFRESH_SECONDS)
def load_data(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ---------------- HEADER ----------------
st.title("🛡️ UPI Fraud Analytics Dashboard")

# ---------------- FILTER ----------------
st.markdown("### 🚨 Recent Alerts / Transactions")

view_type = st.radio(
    label="View",
    options=["Fraud Only", "All Transactions"],
    horizontal=True
)

page = st.number_input(
    "Page",
    min_value=1,
    step=1,
    value=1
)

offset = (page - 1) * PAGE_SIZE

# ---------------- QUERY ----------------
if view_type == "Fraud Only":
    query = f"""
        SELECT *
        FROM audit_logs
        WHERE decision = 'BLOCK'
        ORDER BY timestamp DESC
        LIMIT {PAGE_SIZE} OFFSET {offset}
    """
else:
    query = f"""
        SELECT *
        FROM audit_logs
        ORDER BY timestamp DESC
        LIMIT {PAGE_SIZE} OFFSET {offset}
    """

df = load_data(query)

# ---------------- KPIs ----------------
kpi1, kpi2, kpi3 = st.columns(3)

total_tx = load_data("SELECT COUNT(*) AS c FROM audit_logs")["c"][0]
fraud_tx = load_data(
    "SELECT COUNT(*) AS c FROM audit_logs WHERE decision='BLOCK'"
)["c"][0]

with kpi1:
    st.metric("Total Transactions", total_tx)

with kpi2:
    st.metric("Fraud Transactions", fraud_tx)

with kpi3:
    rate = round((fraud_tx / total_tx) * 100, 2) if total_tx else 0
    st.metric("Fraud Rate (%)", rate)

# ---------------- GRAPHS ----------------
g1, g2, g3 = st.columns(3)

with g1:
    st.markdown("**Risk Score Distribution**")
    st.bar_chart(
        df["risk_score"].value_counts().sort_index(),
        height=200
    )

with g2:
    st.markdown("**Amount Trend**")
    st.line_chart(
        df.sort_values("timestamp")[["amount"]],
        height=200
    )

with g3:
    st.markdown("**Decision Split**")
    st.bar_chart(
        df["decision"].value_counts(),
        height=200
    )

# ---------------- TABLE ----------------
st.markdown("### 📄 Transactions")

if df.empty:
    st.info("No transactions found.")
else:
    st.dataframe(
        df[
            [
                "tx_id",
                "sender_vpa",
                "receiver_vpa",
                "amount",
                "decision",
                "risk_score",
                "confidence",
                "timestamp",
            ]
        ],
        use_container_width=True,
        height=350
    )

# ---------------- AUTO REFRESH ----------------
st.caption(f"🔄 Auto refresh every {REFRESH_SECONDS} seconds")
time.sleep(REFRESH_SECONDS)
st.rerun()
