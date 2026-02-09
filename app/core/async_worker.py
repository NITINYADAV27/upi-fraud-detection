import threading
import json
import time

from app.core.async_queue import transaction_queue
from app.core.database import get_db
from app.core.audit_logger import log_decision
from app.core.redis_client import redis_client

# Redis keys (MUST match main.py)
REDIS_TX_KEY = "recent_transactions"
REVIEW_QUEUE_KEY = "review_queue"


def worker_loop():
    print("🟢 Async Audit Worker started")

    while True:
        payload = transaction_queue.get()

        try:
            """
            payload is expected to be a dict containing:
            {
                tx_id,
                decision,
                risk_score,
                confidence,
                engine_version,
                policy_version,
                latency_ms,
                timestamp,
                sender_vpa,
                receiver_vpa,
                amount
            }
            """

            db = next(get_db())

            # --------------------------------------------------
            # 1️⃣ Immutable audit log (RBI requirement)
            # --------------------------------------------------
            log_decision(payload, payload, db)

            # --------------------------------------------------
            # 2️⃣ Redis push for dashboard (hot data)
            # --------------------------------------------------
            redis_client.lpush(
                REDIS_TX_KEY,
                json.dumps({
                    "tx_id": payload["tx_id"],
                    "amount": payload.get("amount"),
                    "sender_vpa": payload.get("sender_vpa"),
                    "receiver_vpa": payload.get("receiver_vpa"),
                    "decision": payload["decision"],
                    "risk_score": payload["risk_score"],
                    "confidence": payload["confidence"],
                    "latency_ms": payload.get("latency_ms"),
                    "engine_version": payload["engine_version"],
                    "policy_version": payload["policy_version"],
                    "timestamp": payload["timestamp"]
                })
            )

            # Keep only latest 1000 records
            redis_client.ltrim(REDIS_TX_KEY, 0, 999)

            # --------------------------------------------------
            # 3️⃣ REVIEW queue (post-decision workflow)
            # --------------------------------------------------
            if payload["decision"] == "REVIEW":
                redis_client.lpush(
                    REVIEW_QUEUE_KEY,
                    json.dumps({
                        "tx_id": payload["tx_id"],
                        "risk_score": payload["risk_score"],
                        "timestamp": payload["timestamp"]
                    })
                )

            # --------------------------------------------------
            # 4️⃣ Metrics (observability)
            # --------------------------------------------------
            redis_client.incr("metric:total_transactions")
            redis_client.incr(f"metric:decision:{payload['decision']}")

        except Exception as e:
            print("❌ Async worker error:", e)

        finally:
            transaction_queue.task_done()


def start_worker():
    t = threading.Thread(target=worker_loop, daemon=True)
    t.start()



