from app.core.database import Base, engine
from app.models.audit_log import AuditLog

def init():
    Base.metadata.create_all(bind=engine)
    print("Database initialized at fraud_audit.db")

if __name__ == "__main__":
    init()



