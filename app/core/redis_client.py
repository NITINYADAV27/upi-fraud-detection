import os
import redis
import json
from dotenv import load_dotenv

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

# ❌ DEBUG print REMOVE kar diya (production-safe)
if not REDIS_URL:
    raise ValueError(
        "REDIS_URL not found. "
        "Local ke liye .env me rakho, Render pe Environment me set karo."
    )

# --------------------------------------------------
# Redis client (single global instance)
# --------------------------------------------------
redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True
)

# --------------------------------------------------
# Keys used across system
# --------------------------------------------------
TRANSACTION_KEY = "transactions"

# --------------------------------------------------
# WRITE: Store processed transaction
# (used by async_worker)
# --------------------------------------------------
def store_transaction(tx: dict):
    """
    Stores final fraud decision record in Redis.
    Async worker isi ko call karega.
    """
    redis_client.lpush(TRANSACTION_KEY, json.dumps(tx))

# --------------------------------------------------
# READ: Fetch recent transactions
# (used by dashboard / analytics APIs)
# --------------------------------------------------
def fetch_recent_transactions(limit: int = 200):
    """
    Returns list of transaction dicts for analytics/dashboard.
    """
    txs = redis_client.lrange(TRANSACTION_KEY, 0, limit - 1)
    return [json.loads(t) for t in txs]

# --------------------------------------------------
# READ: Fetch all transactions (careful in prod)
# --------------------------------------------------
def fetch_all_transactions():
    txs = redis_client.lrange(TRANSACTION_KEY, 0, -1)
    return [json.loads(t) for t in txs]

# --------------------------------------------------
# HEALTH CHECK (optional but useful)
# --------------------------------------------------
def redis_health_check():
    try:
        redis_client.ping()
        return True
    except Exception:
        return False
