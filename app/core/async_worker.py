import threading
import json
import time
from types import SimpleNamespace

from app.core.async_queue import transaction_queue
from app.core.database import get_db
from app.core.audit_logger import log_decision
from app.core.redis_client import redis_client

# Redis keys (MUST match main.py)
REDIS_TX_KEY = "recent_transactions"
REVIEW_QUEUE_KEY = "review_queue"


def normalize_payload(payload):
    """
    Hard safety layer:
    - dict → object
    - object → object
    """
    if isinstance(payload, dict):
        return SimpleNamespace(**payload)
    return payload


def worker_loop():
    print("🟢 Async Audit Worker started (RBI-compliant)")

    while True:
        raw = transaction_queue.get()
        start_time = time.time()

        try:
            payload = normalize_payload(raw)

            db = next(get_db())

            # --------------------------------------------------
            # 1️⃣ Extract TX + Decision (STRICT CONTRACT)
            # --------------------------------------------------
            tx = SimpleNamespace(
                tx_id=payload.tx_id,
                amount=getattr(payload, "amount", None),
                sender_vpa=getattr(payload, "sender_vpa", None),
                receiver_vpa=getattr(payload, "receiver_vpa", None),
                timestamp=payload.timestamp
            )

            result = {
                "decision": payload.decision,
                "risk_score": payload.risk_score,
                "confidence": payload.confidence,
                "reason": getattr(payload, "reason", None),
            }

            latency_ms = round((time.time() - start_time) * 1000, 2)

            # --------------------------------------------------
            # 2️⃣ Immutable DB audit (RBI mandatory)
            # --------------------------------------------------
            log_decision(tx, result, db)

            # --------------------------------------------------
            # 3️⃣ Redis hot-store (dashboard)
            # --------------------------------------------------
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
                    "latency_ms": latency_ms,
                    "engine_version": getattr(payload, "engine_version", "v1"),
                    "policy_version": getattr(payload, "policy_version", "v1"),
                    "timestamp": tx.timestamp
                })
            )

            redis_client.ltrim(REDIS_TX_KEY, 0, 999)

            # --------------------------------------------------
            # 4️⃣ REVIEW queue (human-in-loop)
            # --------------------------------------------------
            if result["decision"] == "REVIEW":
                redis_client.lpush(
                    REVIEW_QUEUE_KEY,
                    json.dumps({
                        "tx_id": tx.tx_id,
                        "risk_score": result["risk_score"],
                        "timestamp": tx.timestamp
                    })
                )

            # --------------------------------------------------
            # 5️⃣ Metrics (executive observability)
            # --------------------------------------------------
            redis_client.incr("metric:total_transactions")
            redis_client.incr(f"metric:decision:{result['decision']}")

        except Exception as e:
            print("❌ Async audit worker error:", e)

        finally:
            transaction_queue.task_done()


def start_worker():
    t = threading.Thread(target=worker_loop, daemon=True)
    t.start()




