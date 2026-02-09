from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    tx_id = Column(String, index=True, nullable=False)
    amount = Column(Float, nullable=False)

    sender_vpa = Column(String, nullable=False)
    receiver_vpa = Column(String, nullable=False)

    risk_score = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)

    decision = Column(String, index=True, nullable=False)
    reason = Column(String, nullable=True)

    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
