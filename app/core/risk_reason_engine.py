from datetime import datetime

class RiskReasonEngine:
    @staticmethod
    def generate(tx):
        reasons = []

        if tx.first_time_payee:
            reasons.append("FIRST_TIME_PAYEE")

        if tx.geo_risk_score >= 0.8:
            reasons.append("HIGH_GEO_RISK")

        if tx.failed_pin_attempts >= 2:
            reasons.append("MULTIPLE_FAILED_PIN")

        if tx.tx_velocity_5m >= 5:
            reasons.append("HIGH_TX_VELOCITY")

        if tx.account_age_days < 30:
            reasons.append("ACCOUNT_TOO_NEW")

        if tx.avg_tx_30d and tx.amount > tx.avg_tx_30d * 3:
            reasons.append("ABNORMAL_AMOUNT")

        return reasons
