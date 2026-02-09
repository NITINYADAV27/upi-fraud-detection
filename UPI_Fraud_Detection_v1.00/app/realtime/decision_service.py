import time
from app.core.fraud_engine import ProductionFraudEngine
from app.governance.versions import ENGINE_VERSION, POLICY_VERSION

engine = ProductionFraudEngine()

MAX_LATENCY_MS = 40   # hard limit

def decide(tx):
    start = time.perf_counter()

    try:
        result = engine.evaluate_transaction(tx)

        latency_ms = (time.perf_counter() - start) * 1000
        if latency_ms > MAX_LATENCY_MS:
            return fail_open(tx, latency_ms)

        return {
            "tx_id": tx.tx_id,
            "decision": result["action"],
            "risk_score": result["risk_score"],
            "confidence": result["confidence"],
            "engine_version": ENGINE_VERSION,
            "policy_version": POLICY_VERSION
        }

    except Exception:
        return fail_open(tx, 0)


def fail_open(tx, latency):
    return {
        "tx_id": tx.tx_id,
        "decision": "ALLOW",
        "risk_score": 0,
        "confidence": 0.50,
        "engine_version": ENGINE_VERSION,
        "policy_version": POLICY_VERSION,
        "fail_open": True
    }
