from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import DATABASE_URL

# --------------------------------------------------
# SQLAlchemy Engine
# --------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite requirement
    pool_pre_ping=True,                         # safer connections
)

# --------------------------------------------------
# Session factory
# --------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# --------------------------------------------------
# Base class for models
# --------------------------------------------------
Base = declarative_base()

# --------------------------------------------------
# Dependency (FastAPI)
# --------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
