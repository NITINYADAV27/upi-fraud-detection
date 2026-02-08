class ProductionFraudEngine:
    """
    Production-style rule-based fraud engine
    Decisions: ALLOW / REVIEW / BLOCK
    """

    def evaluate_transaction(self, tx):
        risk_score = 0
        risk_factors = []

        # --------------------------------------------------
        # RULE 1: High transaction amount
        # --------------------------------------------------
        if tx.amount >= 20000:
            risk_score += 40
            risk_factors.append("HIGH_AMOUNT")

        elif tx.amount >= 10000:
            risk_score += 25
            risk_factors.append("MEDIUM_AMOUNT")

        # --------------------------------------------------
        # RULE 2: Failed PIN attempts
        # --------------------------------------------------
        if tx.failed_pin_attempts >= 3:
            risk_score += 30
            risk_factors.append("MULTIPLE_FAILED_PIN")

        elif tx.failed_pin_attempts == 2:
            risk_score += 15
            risk_factors.append("FAILED_PIN_ATTEMPTS")

        # --------------------------------------------------
        # RULE 3: Geo risk
        # --------------------------------------------------
        if tx.geo_risk_score >= 80:
            risk_score += 30
            risk_factors.append("HIGH_GEO_RISK")

        elif tx.geo_risk_score >= 50:
            risk_score += 15
            risk_factors.append("MEDIUM_GEO_RISK")

        # --------------------------------------------------
        # RULE 4: Account age
        # --------------------------------------------------
        if tx.account_age_days < 30:
            risk_score += 25
            risk_factors.append("NEW_ACCOUNT")

        elif tx.account_age_days < 90:
            risk_score += 10
            risk_factors.append("RECENT_ACCOUNT")

        # --------------------------------------------------
        # RULE 5: First-time payee
        # --------------------------------------------------
        if tx.first_time_payee:
            risk_score += 20
            risk_factors.append("FIRST_TIME_PAYEE")

        # --------------------------------------------------
        # RULE 6: Transaction velocity
        # --------------------------------------------------
        if tx.tx_velocity_5m >= 5:
            risk_score += 25
            risk_factors.append("HIGH_TX_VELOCITY")

        elif tx.tx_velocity_5m >= 3:
            risk_score += 15
            risk_factors.append("MEDIUM_TX_VELOCITY")

        # --------------------------------------------------
        # RULE 7: Device velocity
        # --------------------------------------------------
        if tx.device_velocity >= 5:
            risk_score += 20
            risk_factors.append("DEVICE_CHANGE_FREQUENT")

        # --------------------------------------------------
        # RULE 8: Spending behavior deviation
        # --------------------------------------------------
        if tx.avg_tx_30d > 0:
            if tx.amount > (tx.avg_tx_30d * 3):
                risk_score += 20
                risk_factors.append("ABNORMAL_AMOUNT_SPIKE")

        # --------------------------------------------------
        # NORMALIZATION
        # --------------------------------------------------
        risk_score = min(risk_score, 100)

        confidence = round(1 - (risk_score / 100), 2)

        # --------------------------------------------------
        # DECISION LOGIC (CORE)
        # --------------------------------------------------
        if risk_score <= 30 and confidence >= 0.8:
            decision = "ALLOW"

        elif 30 < risk_score <= 70:
            decision = "REVIEW"

        else:
            decision = "BLOCK"

        # --------------------------------------------------
        # FINAL RESULT
        # --------------------------------------------------
        return {
            "action": decision,
            "risk_score": risk_score,
            "confidence": confidence,
            "top_risk_factors": risk_factors
        }

