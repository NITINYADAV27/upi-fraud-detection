from app.core.database import engine, Base
from app.models.audit_log import AuditLog

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Done.")

