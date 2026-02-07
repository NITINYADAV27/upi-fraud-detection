import os

API_KEY = os.getenv("API_KEY", "demo-secret-key-123")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///fraud_audit.db"
)

RATE_LIMIT = int(os.getenv("RATE_LIMIT", 20))

ALERT_EMAIL = os.getenv("ALERT_EMAIL", "alerts@example.com")
