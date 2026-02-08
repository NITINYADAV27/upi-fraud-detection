import threading
import json

from app.core.async_queue import transaction_queue
from app.core.fraud_engine import ProductionFraudEngine
from app.core.redis_guard import check_duplicate_tx, check_tx_velocity
from app.core.risk_memory import increase_risk
from app.core.database import get_db
from app.core.audit_logger import log_decision
from app.core.redis_client import redis_client

engine = ProductionFraudEngine()
REDIS_TX_KEY = "recent_transactions"


def normalize(raw: dict):
    return {
        "decision": raw.get("action") or raw.get("decision") or "ALLOW",
        "risk_score": raw.get("risk_score", 0),
        "confidence": raw.get("confidence", 0.5),
        "reason": ",".join(raw.get("top_risk_factors", []))
        if raw.get("top_risk_factors") else raw.get("reason")
    }


def worker_loop():
    print("🟢 Async Fraud Worker started")

    while True:
        tx = transaction_queue.get()

        try:
            db = next(get_db())

            if check_duplicate_tx(tx.tx_id):
                raw = {
                    "action": "BLOCK",
                    "risk_score": 95,
                    "confidence": 0.99,
                    "top_risk_factors": ["DUPLICATE_TRANSACTION"]
                }
                result = normalize(raw)

            elif check_tx_velocity(tx.sender_vpa):
                raw = {
                    "action": "BLOCK",
                    "risk_score": 90,
                    "confidence": 0.95,
                    "top_risk_factors": ["HIGH_TX_VELOCITY"]
                }
                increase_risk(tx.sender_vpa, tx.receiver_vpa, 30)
                result = normalize(raw)

            else:
                raw = engine.evaluate_transaction(tx)
                result = normalize(raw)

                if result["decision"] == "BLOCK":
                    increase_risk(tx.sender_vpa, tx.receiver_vpa, 25)

            # DB write
            log_decision(tx, result, db)

            # 🔥 Redis push
            redis_client.lpush(
                REDIS_TX_KEY,
                json.dumps({
                    "tx_id": tx.tx_id,
                    "amount": tx.amount,
                    "sender_vpa": tx.sender_vpa,
                    "receiver_vpa": tx.receiver_vpa,
                    "decision": result["decision"],
                    "risk_score": result["risk_score"],
                    "confidence": result["confidence"],
                    "timestamp": tx.timestamp
                })
            )

        except Exception as e:
            print("❌ Worker error:", e)

        finally:
            transaction_queue.task_done()


def start_worker():
    t = threading.Thread(target=worker_loop, daemon=True)
    t.start()





