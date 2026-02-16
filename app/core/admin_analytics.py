import sqlite3

DB_PATH = "fraud_audit.db"

def get_connection():
    return sqlite3.connect(DB_PATH)


def get_stats():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM audit_logs")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM audit_logs WHERE decision='BLOCK'")
    blocked = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM audit_logs WHERE decision='STEP_UP_AUTH'")
    step_up = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM audit_logs WHERE decision='ALLOW'")
    allowed = cur.fetchone()[0]

    conn.close()

    return {
        "total_transactions": total,
        "blocked": blocked,
        "step_up": step_up,
        "allowed": allowed
    }


def get_recent_frauds(limit: int = 5):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT tx_id, sender_vpa, receiver_vpa, amount, risk_score, timestamp
        FROM audit_logs
        WHERE decision='BLOCK'
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "tx_id": r[0],
            "sender": r[1],
            "receiver": r[2],
            "amount": r[3],
            "risk_score": r[4],
            "timestamp": r[5]
        }
        for r in rows
    ]
