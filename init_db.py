from app.core.database import engine, Base
from app.models.audit_log import AuditLog

def main():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

if __name__ == "__main__":
    main()
