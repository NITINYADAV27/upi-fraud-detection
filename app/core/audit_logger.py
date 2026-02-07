import json
from datetime import datetime
from app.models.audit_log import AuditLog

def log_decision(tx, result, db):
    record = AuditLog(
        tx_id=tx.tx_id,
        sender_vpa=tx.sender_vpa,
        receiver_vpa=tx.receiver_vpa,
        amount=tx.amount,
        decision=result["action"],
        risk_score=result["risk_score"],
        confidence=result["confidence"],
        risk_factors=json.dumps(result.get("top_risk_factors", [])),
        timestamp=datetime.utcnow().isoformat()
    )

    db.add(record)
    db.commit()
