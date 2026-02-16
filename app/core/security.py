from fastapi import Header, HTTPException
from app.core.config import API_KEY
from app.core.rate_limiter import rate_limit

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )

    # apply rate limiting
    rate_limit(x_api_key)

    return x_api_key
