import os


class ProductionFraudEngine:
    """
    Industry-grade rule-based fraud engine
    Decisions: ALLOW / REVIEW / BLOCK
    Explainable, deterministic, configurable, production-safe
    """

    # ==================================================
    # RISK WEIGHTS (POLICY CONTROLLED)
    # ==================================================
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
        "AMOUNT_SPIKE": 20,
    }

    # ==================================================
    # TRUST / POSITIVE SIGNALS
    # ==================================================
    TRUST_WEIGHTS = {
        "OLD_ACCOUNT_TRUST": 10,
        "NORMAL_SPEND_BEHAVIOR": 10,
    }

    # ==================================================
    # DECISION POLICY (ENV OVERRIDABLE)
    # ==================================================
    ALLOW_MAX_RISK = int(os.getenv("ALLOW_MAX_RISK", 30))
    REVIEW_MAX_RISK = int(os.getenv("REVIEW_MAX_RISK", 70))
    MIN_ALLOW_CONFIDENCE = float(os.getenv("MIN_ALLOW_CONFIDENCE", 0.75))

    MAX_TRUST_REDUCTION = 20   # prevents trust abuse

    # ==================================================
    # CORE EVALUATION
    # ==================================================
    def evaluate_transaction(self, tx):
        risk_score = 0
        trust_score = 0
        risk_factors = []

        # --------------------------------------------------
        # RISK CONTRIBUTION RULES
        # --------------------------------------------------
        if tx.amount >= 20000:
            risk_score += self.RISK_WEIGHTS["HIGH_AMOUNT"]
            risk_factors.append(("HIGH_AMOUNT", +40))
        elif tx.amount >= 10000:
            risk_score += self.RISK_WEIGHTS["MEDIUM_AMOUNT"]
            risk_factors.append(("MEDIUM_AMOUNT", +20))

        if tx.failed_pin_attempts >= 3:
            risk_score += self.RISK_WEIGHTS["FAILED_PIN_HIGH"]
            risk_factors.append(("FAILED_PIN_HIGH", +30))
        elif tx.failed_pin_attempts == 2:
            risk_score += self.RISK_WEIGHTS["FAILED_PIN_MED"]
            risk_factors.append(("FAILED_PIN_MED", +15))

        if tx.geo_risk_score >= 80:
            risk_score += self.RISK_WEIGHTS["HIGH_GEO"]
            risk_factors.append(("HIGH_GEO", +30))
        elif tx.geo_risk_score >= 50:
            risk_score += self.RISK_WEIGHTS["MEDIUM_GEO"]
            risk_factors.append(("MEDIUM_GEO", +15))

        if tx.account_age_days < 30:
            risk_score += self.RISK_WEIGHTS["NEW_ACCOUNT"]
            risk_factors.append(("NEW_ACCOUNT", +25))
        elif tx.account_age_days < 90:
            risk_score += self.RISK_WEIGHTS["RECENT_ACCOUNT"]
            risk_factors.append(("RECENT_ACCOUNT", +10))

        if tx.first_time_payee:
            risk_score += self.RISK_WEIGHTS["FIRST_TIME_PAYEE"]
            risk_factors.append(("FIRST_TIME_PAYEE", +20))

        if tx.tx_velocity_5m >= 5:
            risk_score += self.RISK_WEIGHTS["HIGH_TX_VELOCITY"]
            risk_factors.append(("HIGH_TX_VELOCITY", +25))
        elif tx.tx_velocity_5m >= 3:
            risk_score += self.RISK_WEIGHTS["MEDIUM_TX_VELOCITY"]
            risk_factors.append(("MEDIUM_TX_VELOCITY", +15))

        if tx.device_velocity >= 5:
            risk_score += self.RISK_WEIGHTS["DEVICE_CHANGE"]
            risk_factors.append(("DEVICE_CHANGE", +20))

        if tx.avg_tx_30d > 0 and tx.amount > (tx.avg_tx_30d * 3):
            risk_score += self.RISK_WEIGHTS["AMOUNT_SPIKE"]
            risk_factors.append(("AMOUNT_SPIKE", +20))

        # --------------------------------------------------
        # TRUST / RISK DAMPENING
        # --------------------------------------------------
        if tx.account_age_days > 365:
            trust_score += self.TRUST_WEIGHTS["OLD_ACCOUNT_TRUST"]
            risk_factors.append(("OLD_ACCOUNT_TRUST", -10))

        if tx.avg_tx_30d > 0 and tx.amount <= tx.avg_tx_30d:
            trust_score += self.TRUST_WEIGHTS["NORMAL_SPEND_BEHAVIOR"]
            risk_factors.append(("NORMAL_SPEND_BEHAVIOR", -10))

        trust_score = min(trust_score, self.MAX_TRUST_REDUCTION)
        risk_score = max(risk_score - trust_score, 0)

        # --------------------------------------------------
        # NORMALIZATION & CONFIDENCE
        # --------------------------------------------------
        risk_score = min(risk_score, 100)

        # calibrated confidence (non-linear, realistic)
        confidence = round(max(0.05, 1 - (risk_score / 125)), 2)

        # --------------------------------------------------
        # DECISION POLICY
        # --------------------------------------------------
        if risk_score <= self.ALLOW_MAX_RISK and confidence >= self.MIN_ALLOW_CONFIDENCE:
            decision = "ALLOW"
        elif risk_score <= self.REVIEW_MAX_RISK:
            decision = "REVIEW"
        else:
            decision = "BLOCK"

        # --------------------------------------------------
        # EXPLAINABILITY (ORDERED)
        # --------------------------------------------------
        explainable_factors = [
            f"{name}({impact:+d})" for name, impact in sorted(
                risk_factors, key=lambda x: abs(x[1]), reverse=True
            )
        ]

        return {
            "action": decision,
            "risk_score": risk_score,
            "confidence": confidence,
            "top_risk_factors": explainable_factors
        }

