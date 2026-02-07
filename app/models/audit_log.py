from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    tx_id = Column(String, index=True)
    sender_vpa = Column(String)
    receiver_vpa = Column(String)
    amount = Column(Float)

    decision = Column(String)
    risk_score = Column(Float)
    confidence = Column(Float)
    risk_factors = Column(String)

    actual_label = Column(String, nullable=True)
    timestamp = Column(String)
