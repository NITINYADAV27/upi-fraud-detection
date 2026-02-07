from fastapi import FastAPI
from pydantic import BaseModel

from app.core.async_queue import transaction_queue
from app.core.async_worker import start_worker

app = FastAPI(title="UPI Fraud Detection Engine – Async")

# -------------------------------
# Transaction Schema
# -------------------------------
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
    timestamp: str


# -------------------------------
# Start background worker
# -------------------------------
@app.on_event("startup")
def startup_event():
    start_worker()


# -------------------------------
# API (Producer)
# -------------------------------
@app.post("/v1/decision")
def submit_transaction(tx: TransactionRequest):

    try:
        transaction_queue.put_nowait(tx)
    except Exception:
        return {
            "status": "REJECTED",
            "reason": "QUEUE_FULL"
        }

    return {
        "status": "ACCEPTED",
        "message": "Transaction queued for fraud analysis"
    }
