from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    tx_id = Column(String, index=True)
    decision = Column(String)
    reason = Column(String)
    amount = Column(Float)
    sender_vpa = Column(String)
    receiver_vpa = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


