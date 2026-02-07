from pydantic import BaseModel, Field
from typing import Optional
import datetime

class UPITransaction(BaseModel):
    tx_id: str
    amount: float
    sender_vpa: str
    receiver_vpa: str
    geo_risk_score: float = 0.0
    failed_pin_attempts: int = 0
    account_age_days: int = 0
    device_velocity: int = 0
    tx_velocity_5m: int = 0
    avg_tx_30d: Optional[float] = None
    first_time_payee: bool = False
    high_value_ratio: float = 1.0
    timestamp: Optional[datetime.datetime] = None
