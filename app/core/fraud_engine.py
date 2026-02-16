import os
import math
from app.core.onnx_engine import ONNXFraudModel


class ProductionFraudEngine:
    """
    Industry-grade HYBRID fraud engine

    Authority order:
    1. Hard rules (RBI / policy)
    2. Risk score
    3. ML probability (risk amplifier, fail-open)

    Decisions: ALLOW / REVIEW / BLOCK
    """

    # ==================================================
    # RULE WEIGHTS
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

    TRUST_WEIGHTS = {
        "OLD_ACCOUNT_TRUST": 10,
        "NORMAL_SPEND": 10,
    }

    # ==================================================
    # POLICY (ENV OVERRIDABLE)
    # ==================================================
    ALLOW_MAX_RISK = int(os.getenv("ALLOW_MAX_RISK", 30))
    REVIEW_MAX_RISK = int(os.getenv("REVIEW_MAX_RISK", 70))
    MIN_ALLOW_CONFIDENCE = float(os.getenv("MIN_ALLOW_CONFIDENCE", 0.75))

    ML_BLOCK_THRESHOLD = float(os.getenv("ML_BLOCK_THRESHOLD", 0.85))
    ML_REVIEW_THRESHOLD = float(os.getenv("ML_REVIEW_THRESHOLD", 0.45))

    MAX_TRUST_REDUCTION = 20

    # ==================================================
    # INIT
    # ==================================================
    def __init__(self):
        self.ml = ONNXFraudModel(
            os.getenv("ONNX_MODEL_PATH", "app/core/fraud_model.onnx")
        )

    # ==================================================
    # FEATURE PREPARATION (MUST MATCH ONNX TRAINING)
    # ==================================================
    def _prepare_ml_features(self, tx):
        return [
            float(tx.geo_risk_score),
            float(tx.failed_pin_attempts),
            min(float(tx.account_age_days), 365.0) / 365.0,
            min(float(tx.device_velocity), 60.0) / 60.0,
            min(float(tx.tx_velocity_5m), 20.0) / 20.0,
            float(tx.high_value_ratio),
            1.0 if tx.first_time_payee else 0.0,
            float(math.log1p(tx.amount)),
        ]

    # ==================================================
    # CORE DECISION ENGINE
    # ==================================================
    def evaluate_transaction(self, tx):
        risk_score = 0
        trust_score = 0
        factors = []

        # ---------------- RULES ----------------
        if tx.amount >= 20000:
            risk_score += 40
            factors.append(("HIGH_AMOUNT", +40))
        elif tx.amount >= 10000:
            risk_score += 20
            factors.append(("MEDIUM_AMOUNT", +20))

        if tx.failed_pin_attempts >= 3:
            risk_score += 30
            factors.append(("FAILED_PIN_HIGH", +30))
        elif tx.failed_pin_attempts == 2:
            risk_score += 15
            factors.append(("FAILED_PIN_MED", +15))

        if tx.geo_risk_score >= 80:
            risk_score += 30
            factors.append(("HIGH_GEO", +30))
        elif tx.geo_risk_score >= 50:
            risk_score += 15
            factors.append(("MEDIUM_GEO", +15))

        if tx.account_age_days < 30:
            risk_score += 25
            factors.append(("NEW_ACCOUNT", +25))
        elif tx.account_age_days < 90:
            risk_score += 10
            factors.append(("RECENT_ACCOUNT", +10))

        if tx.first_time_payee:
            risk_score += 20
            factors.append(("FIRST_TIME_PAYEE", +20))

        if tx.tx_velocity_5m >= 5:
            risk_score += 25
            factors.append(("HIGH_TX_VELOCITY", +25))
        elif tx.tx_velocity_5m >= 3:
            risk_score += 15
            factors.append(("MEDIUM_TX_VELOCITY", +15))

        if tx.device_velocity >= 5:
            risk_score += 20
            factors.append(("DEVICE_CHANGE", +20))

        if tx.avg_tx_30d > 0 and tx.amount > tx.avg_tx_30d * 3:
            risk_score += 20
            factors.append(("AMOUNT_SPIKE", +20))

        # ---------------- TRUST ----------------
        if tx.account_age_days > 365:
            trust_score += 10
            factors.append(("OLD_ACCOUNT_TRUST", -10))

        if tx.avg_tx_30d > 0 and tx.amount <= tx.avg_tx_30d:
            trust_score += 10
            factors.append(("NORMAL_SPEND", -10))

        trust_score = min(trust_score, self.MAX_TRUST_REDUCTION)
        risk_score = max(risk_score - trust_score, 0)
        risk_score = min(risk_score, 100)

        # ---------------- CONFIDENCE ----------------
        confidence = round(max(0.05, 1 - (risk_score / 125)), 2)

        # ---------------- ML (FAIL-OPEN) ----------------
        ml_features = self._prepare_ml_features(tx)
        ml_score = float(self.ml.predict_proba(ml_features))

        # ---------------- FINAL DECISION ----------------
        if ml_score >= self.ML_BLOCK_THRESHOLD:
            decision = "BLOCK"
            factors.append(("ML_HIGH_RISK", +int(ml_score * 100)))

        elif ml_score >= self.ML_REVIEW_THRESHOLD:
            decision = "REVIEW"
            factors.append(("ML_MEDIUM_RISK", +int(ml_score * 100)))

        else:
            if risk_score <= self.ALLOW_MAX_RISK and confidence >= self.MIN_ALLOW_CONFIDENCE:
                decision = "ALLOW"
            elif risk_score <= self.REVIEW_MAX_RISK:
                decision = "REVIEW"
            else:
                decision = "BLOCK"

        # ---------------- EXPLAINABILITY ----------------
        explainable = [
            f"{k}({v:+d})"
            for k, v in sorted(factors, key=lambda x: abs(x[1]), reverse=True)
        ]

        return {
            "action": decision,
            "risk_score": max(risk_score, int(ml_score * 100)),
            "confidence": confidence,
            "ml_score": round(ml_score, 4),
            "top_risk_factors": explainable,
        }
