import os
from dotenv import load_dotenv

# --------------------------------------------------
# Load .env explicitly (IMPORTANT for Windows)
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# Base directory
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# --------------------------------------------------
# Database (Audit logs)
# --------------------------------------------------
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'fraud_audit.db')}"

# --------------------------------------------------
# Redis (Required)
# --------------------------------------------------
REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    raise RuntimeError(
        "REDIS_URL environment variable not set. "
        "Local: use .env | Production: set in Render dashboard."
    )
