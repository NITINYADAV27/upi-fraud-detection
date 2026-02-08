from app.core.risk_memory import get_risk

class ProductionFraudEngine:

    def evaluate_transaction(self, tx):
        risk = 0
        factors = []

        # 🔁 Dynamic Redis Risk Memory
        dynamic_risk = get_risk(tx.sender_vpa, tx.receiver_vpa)
        if dynamic_risk > 0:
            risk += dynamic_risk
            factors.append("HISTORICAL_RISK")

        # Rule-based checks
        if tx.amount > 10000:
            risk += 40
            factors.append("HIGH_AMOUNT")

        if tx.first_time_payee:
            risk += 20
            factors.append("FIRST_TIME_PAYEE")

        if tx.failed_pin_attempts >= 3:
            risk += 30
            factors.append("MULTIPLE_FAILED_PIN")

        action = "ALLOW"
        confidence = 0.6

        if risk >= 70:
            action = "BLOCK"
            confidence = 0.95

        return {
            "action": action,
            "risk_score": min(risk, 100),
            "confidence": confidence,
            "top_risk_factors": factors
        }
