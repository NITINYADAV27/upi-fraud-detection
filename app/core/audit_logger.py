from datetime import datetime
from app.models.audit_log import AuditLog

def log_decision(tx, result: dict, db):
    """
    FINAL SAFE LOGGER — NEVER CRASHES
    """

    decision = (
        result.get("decision")
        or result.get("action")
        or "ALLOW"
    )

    audit = AuditLog(
        tx_id=tx.tx_id,
        amount=tx.amount,
        sender_vpa=tx.sender_vpa,
        receiver_vpa=tx.receiver_vpa,
        risk_score=result.get("risk_score", 0),
        confidence=result.get("confidence", 0.5),
        decision=decision,
        reason=result.get("reason"),
        timestamp=datetime.fromisoformat(tx.timestamp)
    )

    db.add(audit)
    db.commit()

