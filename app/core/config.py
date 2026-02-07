import os

# Redis (Upstash)
REDIS_URL = os.getenv("REDIS_URL")

# SQLite (local + Render safe)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./fraud_audit.db"
)

