from app.core.database import Base, engine
from app.models.audit_log import AuditLog

def init():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully (fraud_audit.db)")
    except Exception as e:
        print("❌ Database initialization failed:", e)
        raise

if __name__ == "__main__":
    init()
