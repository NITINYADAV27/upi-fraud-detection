import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'fraud_audit.db')}"

REDIS_URL = os.getenv("REDIS_URL")
