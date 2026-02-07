from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.core.async_queue import transaction_queue
from app.core.async_worker import start_worker

# --------------------------------------------------
# App init
# --------------------------------------------------
app = FastAPI(
    title="UPI Fraud Detection Engine – Async",
    version="1.0.0"
)

# --------------------------------------------------
# API Key security (simple & production-safe)
# --------------------------------------------------
API_KEY = "upi_fraud_prod_2026_secure_key"   # keep same as before

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
# Decision API (Producer)
# --------------------------------------------------
@app.post("/v1/decision")
def submit_transaction(
    tx: TransactionRequest,
    _: None = Depends(verify_api_key)
):
    try:
        # add timestamp if client didn’t send
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
