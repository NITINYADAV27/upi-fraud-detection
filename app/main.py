from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json

from app.core.async_queue import transaction_queue
from app.core.async_worker import start_worker
from app.core.redis_client import redis_client   # already exists in your project

# --------------------------------------------------
# App init
# --------------------------------------------------
app = FastAPI(
    title="UPI Fraud Detection Engine – Async",
    version="1.0.0"
)

# --------------------------------------------------
# CORS (REQUIRED for frontend & Render)
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# API Key security
# --------------------------------------------------
import os
API_KEY = os.getenv("API_KEY", "upi_fraud_prod_2026_secure_key")

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# --------------------------------------------------
# Transaction Schema
# --------------------------------------------------
class TransactionRequest(BaseModel):
    tx_id: str
    amount: float
    sender_vpa: str
    receiver_vpa: str

    geo_risk_score: int = 0
    failed_pin_attempts: int = 0
    account_age_days: int = 0
    device_velocity: int = 0
    tx_velocity_5m: int = 0
    avg_tx_30d: float = 0
    first_time_payee: bool = False
    high_value_ratio: float = 0

    timestamp: Optional[str] = None

# --------------------------------------------------
# Startup – start async fraud worker
# --------------------------------------------------
@app.on_event("startup")
def startup_event():
    start_worker()

# --------------------------------------------------
# Health check (IMPORTANT for Render)
# --------------------------------------------------
@app.get("/")
def health_check():
    return {
        "status": "UP",
        "service": "UPI Fraud Detection Engine",
        "mode": "async"
    }

# --------------------------------------------------
# Decision API (ASYNC PRODUCER)
# --------------------------------------------------
@app.post("/v1/decision")
def submit_transaction(
    tx: TransactionRequest,
    _: None = Depends(verify_api_key)
):
    try:
        if not tx.timestamp:
            tx.timestamp = datetime.utcnow().isoformat()

        transaction_queue.put_nowait(tx)

    except Exception:
        return {
            "status": "REJECTED",
            "reason": "QUEUE_FULL"
        }

    return {
        "status": "ACCEPTED",
        "message": "Transaction queued for fraud analysis",
        "tx_id": tx.tx_id
    }

# ==================================================
# 🔥 NEW — PRODUCT / DASHBOARD APIs (SAFE)
# ==================================================

REDIS_TX_KEY = "transactions"   # already used by worker

# --------------------------------------------------
# Get all processed transactions (Frontend table)
# --------------------------------------------------
@app.get("/api/transactions")
def get_transactions(limit: int = 200):
    txs = redis_client.lrange(REDIS_TX_KEY, 0, limit)
    return [json.loads(t) for t in txs]

# --------------------------------------------------
# Analytics: stats (metrics cards)
# --------------------------------------------------
@app.get("/api/analytics/stats")
def analytics_stats():
    txs = [json.loads(t) for t in redis_client.lrange(REDIS_TX_KEY, 0, -1)]

    total = len(txs)
    fraud = len([t for t in txs if t.get("decision") == "BLOCK"])
    rate = round((fraud / total) * 100, 2) if total else 0

    return {
        "total_transactions": total,
        "fraud_transactions": fraud,
        "fraud_rate": rate
    }

# --------------------------------------------------
# Analytics: decision split (chart)
# --------------------------------------------------
@app.get("/api/analytics/decision-split")
def analytics_decision_split():
    txs = [json.loads(t) for t in redis_client.lrange(REDIS_TX_KEY, 0, -1)]

    return {
        "ALLOW": sum(1 for t in txs if t.get("decision") == "ALLOW"),
        "BLOCK": sum(1 for t in txs if t.get("decision") == "BLOCK"),
        "REVIEW": sum(1 for t in txs if t.get("decision") == "REVIEW"),
    }

# --------------------------------------------------
# Analytics: risk score distribution (chart)
# --------------------------------------------------
@app.get("/api/analytics/risk-distribution")
def analytics_risk_distribution():
    txs = [json.loads(t) for t in redis_client.lrange(REDIS_TX_KEY, 0, -1)]
    return [t.get("risk_score", 0) for t in txs]
