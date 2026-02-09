from fastapi import APIRouter, HTTPException
from datetime import datetime
from core.fraud_engine import evaluate_transaction
from core.redis_client import store_transaction, fetch_recent_transactions

router = APIRouter(prefix="/api", tags=["Public API"])

@router.post("/decision")
def decision(tx: dict):
    try:
        result = evaluate_transaction(tx)

        record = {
            **tx,
            **result,
            "timestamp": datetime.utcnow().isoformat()
        }

        store_transaction(record)
        return record

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transactions")
def transactions(limit: int = 100):
    return fetch_recent_transactions(limit)
