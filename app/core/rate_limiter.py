# app/core/rate_limiter.py

import time
from collections import defaultdict
from fastapi import HTTPException

# requests per minute
RATE_LIMIT = 20

# { api_key: [timestamps] }
_request_log = defaultdict(list)

def rate_limit(api_key: str):
    now = time.time()
    window_start = now - 60

    timestamps = _request_log[api_key]

    # remove old timestamps
    _request_log[api_key] = [t for t in timestamps if t > window_start]

    if len(_request_log[api_key]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later."
        )

    _request_log[api_key].append(now)
