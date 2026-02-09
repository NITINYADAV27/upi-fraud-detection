from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import json
import os
import time

from app.core.async_queue import transaction_queue
from app.core.async_worker import start_worker
from app.core.redis_client import redis_client
from app.core.fraud_engine import ProductionFraudEngine

# ==================================================
# App init
# ==================================================
app = FastAPI(
    title="UPI Fraud Detection Engine",
    version="1.2.0"
)

# ==================================================
# CORS
# ==================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================================================
# Security
# ==================================================
API_KEY = os.getenv("API_KEY", "upi_fraud_prod_2026_secure_key")

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# ==================================================
# Engine & governance
# ==================================================
engine = ProductionFraudEngine()

ENGINE_VERSION = "1.2.0"
POLICY_VERSION = "upi_risk_policy_2026_01"
MAX_LATENCY_MS = 50

REDIS_TX_KEY = "recent_transactions"
REVIEW_QUEUE_KEY = "review_queue"

# ==================================================
# Transaction schema
# ==================================================
class TransactionRequest(BaseModel):
    tx_id: str = Field(..., min_length=4)
    amount: float = Field(..., gt=0)

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

# ==================================================
# Startup
# ==================================================
@app.on_event("startup")
def startup_event():
    start_worker()

# ==================================================
# Health
# ==================================================
@app.get("/")
def health():
    return {"status": "UP"}

# ==================================================
# 🔥 REAL-TIME DECISION API (≤50 ms, FINAL AUTHORITY)
# ==================================================
@app.post("/v1/decision")
def decision_api(
    tx: TransactionRequest,
    _: None = Depends(verify_api_key)
):
    start = time.perf_counter()

    if not tx.timestamp:
        tx.timestamp = datetime.utcnow().isoformat()

    try:
        result = engine.evaluate_transaction(tx)
        decision = result["action"]

    except Exception:
        # FAIL-OPEN (RBI safe)
        decision = "ALLOW"
        result = {
            "risk_score": 0,
            "confidence": 0.5,
            "top_risk_factors": ["FAIL_OPEN"]
        }

    latency_ms = (time.perf_counter() - start) * 1000

    if latency_ms > MAX_LATENCY_MS:
        decision = "ALLOW"
        result["top_risk_factors"].append("LATENCY_FAIL_OPEN")

    response = {
        "tx_id": tx.tx_id,
        "decision": decision,
        "risk_score": result["risk_score"],
        "confidence": result["confidence"],
        "engine_version": ENGINE_VERSION,
        "policy_version": POLICY_VERSION,
        "latency_ms": round(latency_ms, 2),
        "timestamp": tx.timestamp
    }

    # --------------------------------------------------
    # 🔹 Metrics (real-time counters)
    # --------------------------------------------------
    redis_client.incr("metric:total_transactions")
    redis_client.incr(f"metric:decision:{decision}")

    # --------------------------------------------------
    # 🔹 REVIEW workflow
    # --------------------------------------------------
    if decision == "REVIEW":
        redis_client.lpush(
            REVIEW_QUEUE_KEY,
            json.dumps(response)
        )

    # --------------------------------------------------
    # 🔹 Async audit + dashboard
    # --------------------------------------------------
    transaction_queue.put_nowait({
        **response,
        "sender_vpa": tx.sender_vpa,
        "receiver_vpa": tx.receiver_vpa,
        "amount": tx.amount
    })

    return response

# ==================================================
# DASHBOARD / ANALYTICS
# ==================================================
@app.get("/api/transactions")
def get_transactions(limit: int = 200):
    raw = redis_client.lrange(REDIS_TX_KEY, 0, limit - 1)
    return [json.loads(r) for r in raw]

@app.get("/api/analytics/stats")
def analytics_stats():
    txs = [json.loads(r) for r in redis_client.lrange(REDIS_TX_KEY, 0, -1)]
    total = len(txs)
    fraud = sum(1 for t in txs if t["decision"] == "BLOCK")
    return {
        "total_transactions": total,
        "fraud_transactions": fraud,
        "fraud_rate": round((fraud / total) * 100, 2) if total else 0
    }

@app.get("/api/analytics/decision-split")
def decision_split():
    txs = [json.loads(r) for r in redis_client.lrange(REDIS_TX_KEY, 0, -1)]
    return {
        "ALLOW": sum(1 for t in txs if t["decision"] == "ALLOW"),
        "REVIEW": sum(1 for t in txs if t["decision"] == "REVIEW"),
        "BLOCK": sum(1 for t in txs if t["decision"] == "BLOCK"),
    }

@app.get("/api/analytics/risk-distribution")
def risk_distribution():
    txs = [json.loads(r) for r in redis_client.lrange(REDIS_TX_KEY, 0, -1)]
    return [t.get("risk_score", 0) for t in txs]

# ==================================================
# REVIEW MANAGEMENT
# ==================================================
@app.get("/api/review/queue")
def review_queue(limit: int = 50):
    raw = redis_client.lrange(REVIEW_QUEUE_KEY, 0, limit - 1)
    return [json.loads(r) for r in raw]

@app.post("/api/review/decision")
def review_decision(tx_id: str, decision: str):
    decision = decision.upper()
    if decision not in ("ALLOW", "BLOCK"):
        raise HTTPException(status_code=400, detail="Invalid decision")

    redis_client.lpush(
        "review_decisions",
        json.dumps({
            "tx_id": tx_id,
            "final_decision": decision,
            "timestamp": datetime.utcnow().isoformat()
        })
    )

    return {"status": "UPDATED", "tx_id": tx_id, "decision": decision}

# ==================================================
# METRICS
# ==================================================
@app.get("/api/metrics")
def metrics():
    return {
        "total": int(redis_client.get("metric:total_transactions") or 0),
        "allow": int(redis_client.get("metric:decision:ALLOW") or 0),
        "review": int(redis_client.get("metric:decision:REVIEW") or 0),
        "block": int(redis_client.get("metric:decision:BLOCK") or 0),
    }


