import os

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../..")
)

# Raw DB file path (for sqlite3)
DB_PATH = os.path.join(BASE_DIR, "fraud_audit.db")

# SQLAlchemy-compatible URL
DATABASE_URL = f"sqlite:///{DB_PATH}"

