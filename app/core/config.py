import os

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../..")
)

DB_PATH = os.path.join(BASE_DIR, "fraud_audit.db")

# ✅ Alias for backward compatibility
DATABASE_URL = DB_PATH
