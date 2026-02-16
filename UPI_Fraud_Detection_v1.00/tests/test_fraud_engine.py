from app.core.fraud_engine import ProductionFraudEngine


class DummyTx:
    def __init__(
        self,
        amount=0,
        failed_pin_attempts=0,
        geo_risk_score=0,
        account_age_days=0,
        first_time_payee=False,
        tx_velocity_5m=0,
        device_velocity=0,
        avg_tx_30d=0
    ):
        self.amount = amount
        self.failed_pin_attempts = failed_pin_attempts
        self.geo_risk_score = geo_risk_score
        self.account_age_days = account_age_days
        self.first_time_payee = first_time_payee
        self.tx_velocity_5m = tx_velocity_5m
        self.device_velocity = device_velocity
        self.avg_tx_30d = avg_tx_30d


engine = ProductionFraudEngine()


def test_allow_transaction():
    tx = DummyTx(
        amount=300,
        account_age_days=800,
        avg_tx_30d=500
    )
    result = engine.evaluate_transaction(tx)
    assert result["action"] == "ALLOW"


def test_review_transaction():
    tx = DummyTx(
        amount=9000,
        account_age_days=60,
        first_time_payee=True
    )
    result = engine.evaluate_transaction(tx)
    assert result["action"] == "REVIEW"


def test_block_transaction():
    tx = DummyTx(
        amount=50000,
        failed_pin_attempts=4,
        geo_risk_score=90,
        account_age_days=5
    )
    result = engine.evaluate_transaction(tx)
    assert result["action"] == "BLOCK"
