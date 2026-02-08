import threading
import time

from app.core.async_queue import transaction_queue
from app.core.fraud_engine import ProductionFraudEngine
from app.core.redis_guard import check_duplicate_tx, check_tx_velocity
from app.core.risk_memory import increase_risk
from app.core.database import get_db
from app.core.audit_logger import log_decision

engine = ProductionFraudEngine()

def worker_loop():
    print("🟢 Async Fraud Worker started")

    while True:
        tx = transaction_queue.get()

        try:
            db = get_db()

            # 1️⃣ Duplicate protection
            if check_duplicate_tx(tx.tx_id):
                result = {
                    "action": "BLOCK",
                    "risk_score": 95,
                    "confidence": 0.99,
                    "top_risk_factors": ["DUPLICATE_TRANSACTION"]
                }
                log_decision(tx, result, db)
                continue

            # 2️⃣ Velocity protection
            if check_tx_velocity(tx.sender_vpa):
                result = {
                    "action": "BLOCK",
                    "risk_score": 90,
                    "confidence": 0.95,
                    "top_risk_factors": ["HIGH_TX_VELOCITY"]
                }
                increase_risk(tx.sender_vpa, tx.receiver_vpa, 30)
                log_decision(tx, result, db)
                continue

            # 3️⃣ Core fraud logic
            result = engine.evaluate_transaction(tx)

            if result["action"] == "BLOCK":
                increase_risk(tx.sender_vpa, tx.receiver_vpa, 25)

            log_decision(tx, result, db)

        except Exception as e:
            print("❌ Worker error:", e)

        finally:
            transaction_queue.task_done()


def start_worker():
    t = threading.Thread(target=worker_loop, daemon=True)
    t.start()
