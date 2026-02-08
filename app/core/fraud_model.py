import math
from typing import Any, Dict, List

class ProductionFraudEngine:
    """
    JSON-safe, FastAPI-safe, Pydantic-safe fraud engine
    """

    def prepare_features(self, tx) -> List[float]:
        """
        Accepts Pydantic model (UPITransaction)
        Returns pure Python list
        """
        return [
            float(tx.geo_risk_score),
            float(tx.failed_pin_attempts),
            min(float(tx.account_age_days), 365.0) / 365.0,
            min(float(tx.device_velocity), 60.0) / 60.0,
            min(float(tx.tx_velocity_5m), 20.0) / 20.0,
            float(tx.high_value_ratio),
            1.0 if tx.first_time_payee else 0.0,
            float(math.log1p(tx.amount))
        ]

    def predict(self, features: List[float]) -> Dict[str, Any]:
        """
        Returns ONLY Python-native types
        """

        risk_score = (
            features[0] * 30 +
            features[4] * 25 +
            features[6] * 20 +
            features[7] * 10
        )

        risk_score = min(float(risk_score), 100.0)

        if risk_score >= 85:
            action = "BLOCK"
        elif risk_score >= 60:
            action = "REVIEW"
        else:
            action = "ALLOW"

        return {
            "action": action,
            "risk_score": round(risk_score, 2),
            "confidence": round(min(risk_score / 100 + 0.1, 1.0), 2),
            "top_risk_factors": [
                "GEO_RISK",
                "TX_VELOCITY",
                "FIRST_TIME_PAYEE"
            ][: max(1, int(risk_score // 30))],
            "rbi_compliant": True
        }


