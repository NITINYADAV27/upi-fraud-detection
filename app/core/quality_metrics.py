import sqlite3

DB_PATH = "fraud_audit.db"

def update_actual_label(tx_id: str, label: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        UPDATE audit_logs
        SET actual_label = ?
        WHERE tx_id = ?
    """, (label, tx_id))

    conn.commit()
    conn.close()
