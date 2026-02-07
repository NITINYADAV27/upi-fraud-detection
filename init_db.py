import sqlite3
from app.core.config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tx_id TEXT,
    amount REAL,
    sender_vpa TEXT,
    receiver_vpa TEXT,
    decision TEXT,
    risk_score INTEGER,
    timestamp TEXT
)
""")

conn.commit()
conn.close()

print("DB initialized:", DB_PATH)
