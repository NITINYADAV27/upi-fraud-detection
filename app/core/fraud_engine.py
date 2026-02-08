class ProductionFraudEngine:
    """
    Industry-grade rule-based fraud engine
    Decisions: ALLOW / REVIEW / BLOCK
    Explainable, deterministic, configurable
    """

    # -------------------------------
    # Risk Weights (Policy Driven)
    # -------------------------------
    RISK_WEIGHTS = {
        "HIGH_AMOUNT": 40,
        "MEDIUM_AMOUNT": 20,

        "FAILED_PIN_HIGH": 30,
        "FAILED_PIN_MED": 15,

        "HIGH_GEO": 30,
        "MEDIUM_GEO": 15,

        "NEW_ACCOUNT": 25,
        "RECENT_ACCOUNT": 10,

        "FIRST_TIME_PAYEE": 20,

        "HIGH_TX_VELOCITY": 25,
        "MEDIUM_TX_VELOCITY": 15,

        "DEVICE_CHANGE": 20,
        "AMOUNT_SPIKE": 20
    }

    # -------------------------------
    # Trust Reductions (Positive)
    # -------------------------------
    TRUST_WEIGHTS = {
        "OLD_ACCOUNT_TRUST": 10,
        "NORMAL_SPEND_BEHAVIOR": 10
    }

    # -------------------------------
    # Decision Thresholds
    # -------------------------------
    DECISION_POLICY = {
        "ALLOW_MAX_RISK": 30,
        "REVIEW_MAX_RISK": 70,
        "MIN_ALLOW_CONFIDENCE": 0.75
    }

    def evaluate_transaction(self, tx):
        risk_score = 0
        risk_factors = []

        # ==================================================
        # RISK CONTRIBUTION RULES
        # ==================================================

        # Amount risk
        if tx.amount >= 20000:
            risk_score += self.RISK_WEIGHTS["HIGH_AMOUNT"]
            risk_factors.append("HIGH_AMOUNT(+40)")
        elif tx.amount >= 10000:
            risk_score += self.RISK_WEIGHTS["MEDIUM_AMOUNT"]
            risk_factors.append("MEDIUM_AMOUNT(+20)")

        # Failed PIN attempts
        if tx.failed_pin_attempts >= 3:
            risk_score += self.RISK_WEIGHTS["FAILED_PIN_HIGH"]
            risk_factors.append("FAILED_PIN_HIGH(+30)")
        elif tx.failed_pin_attempts == 2:
            risk_score += self.RISK_WEIGHTS["FAILED_PIN_MED"]
            risk_factors.append("FAILED_PIN_MED(+15)")

        # Geo risk
        if tx.geo_risk_score >= 80:
            risk_score += self.RISK_WEIGHTS["HIGH_GEO"]
            risk_factors.append("HIGH_GEO(+30)")
        elif tx.geo_risk_score >= 50:
            risk_score += self.RISK_WEIGHTS["MEDIUM_GEO"]
            risk_factors.append("MEDIUM_GEO(+15)")

        # Account age
        if tx.account_age_days < 30:
            risk_score += self.RISK_WEIGHTS["NEW_ACCOUNT"]
            risk_factors.append("NEW_ACCOUNT(+25)")
        elif tx.account_age_days < 90:
            risk_score += self.RISK_WEIGHTS["RECENT_ACCOUNT"]
            risk_factors.append("RECENT_ACCOUNT(+10)")

        # First-time payee
        if tx.first_time_payee:
            risk_score += self.RISK_WEIGHTS["FIRST_TIME_PAYEE"]
            risk_factors.append("FIRST_TIME_PAYEE(+20)")

        # Transaction velocity
        if tx.tx_velocity_5m >= 5:
            risk_score += self.RISK_WEIGHTS["HIGH_TX_VELOCITY"]
            risk_factors.append("HIGH_TX_VELOCITY(+25)")
        elif tx.tx_velocity_5m >= 3:
            risk_score += self.RISK_WEIGHTS["MEDIUM_TX_VELOCITY"]
            risk_factors.append("MEDIUM_TX_VELOCITY(+15)")

        # Device velocity
        if tx.device_velocity >= 5:
            risk_score += self.RISK_WEIGHTS["DEVICE_CHANGE"]
            risk_factors.append("DEVICE_CHANGE(+20)")

        # Spending anomaly
        if tx.avg_tx_30d > 0 and tx.amount > (tx.avg_tx_30d * 3):
            risk_score += self.RISK_WEIGHTS["AMOUNT_SPIKE"]
            risk_factors.append("AMOUNT_SPIKE(+20)")

        # ==================================================
        # TRUST / RISK DAMPENING
        # ==================================================
        if tx.account_age_days > 365:
            risk_score -= self.TRUST_WEIGHTS["OLD_ACCOUNT_TRUST"]
            risk_factors.append("OLD_ACCOUNT_TRUST(-10)")

        if tx.avg_tx_30d > 0 and tx.amount <= tx.avg_tx_30d:
            risk_score -= self.TRUST_WEIGHTS["NORMAL_SPEND_BEHAVIOR"]
            risk_factors.append("NORMAL_SPEND_BEHAVIOR(-10)")

        # Ensure non-negative risk
        risk_score = max(risk_score, 0)

        # ==================================================
        # NORMALIZATION & CONFIDENCE
        # ==================================================
        risk_score = min(risk_score, 100)
        confidence = round(max(0.05, 1 - (risk_score / 120)), 2)

        # ==================================================
        # DECISION ENGINE (INDUSTRY STANDARD)
        # ==================================================
        if (
            risk_score <= self.DECISION_POLICY["ALLOW_MAX_RISK"]
            and confidence >= self.DECISION_POLICY["MIN_ALLOW_CONFIDENCE"]
        ):
            decision = "ALLOW"

        elif risk_score <= self.DECISION_POLICY["REVIEW_MAX_RISK"]:
            decision = "REVIEW"

        else:
            decision = "BLOCK"

        return {
            "action": decision,
            "risk_score": risk_score,
            "confidence": confidence,
            "top_risk_factors": risk_factors
        }






