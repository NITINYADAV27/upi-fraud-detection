import time
from app.core.redis_client import redis_client

TX_ID_TTL = 300        # 5 minutes
USER_WINDOW = 60       # 1 minute
MAX_TX_PER_MIN = 5     # threshold

def check_duplicate_tx(tx_id: str):
    key = f"tx:{tx_id}"
    if redis_client.exists(key):
        return True
    redis_client.setex(key, TX_ID_TTL, "1")
    return False


def check_tx_velocity(sender_vpa: str):
    key = f"user:{sender_vpa}:tx_count"
    count = redis_client.incr(key)

    if count == 1:
        redis_client.expire(key, USER_WINDOW)

    return count > MAX_TX_PER_MIN
