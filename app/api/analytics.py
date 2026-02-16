from fastapi import APIRouter
from core.redis_client import fetch_recent_transactions

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/stats")
def stats():
    txs = fetch_recent_transactions(1000)

    total = len(txs)
    fraud = sum(1 for t in txs if t["decision"] == "BLOCK")
    rate = round((fraud / total) * 100, 2) if total else 0

    return {
        "total_transactions": total,
        "fraud_transactions": fraud,
        "fraud_rate": rate
    }


@router.get("/decision-split")
def decision_split():
    txs = fetch_recent_transactions(1000)
    return {
        "ALLOW": sum(1 for t in txs if t["decision"] == "ALLOW"),
        "BLOCK": sum(1 for t in txs if t["decision"] == "BLOCK"),
        "REVIEW": sum(1 for t in txs if t["decision"] == "REVIEW")
    }
