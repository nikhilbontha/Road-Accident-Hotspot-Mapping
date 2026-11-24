import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Determine database URL. If postgres is unreachable or in sqlite dev mode, support sqlite fallback
DATABASE_URL = settings.DATABASE_URL

# For SQLite, connect_args is needed
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
    # Test connection
    with engine.connect() as conn:
        pass
except Exception:
    # Fallback to local SQLite for development/testing when PostgreSQL is not running
    SQLITE_URL = "sqlite:///./road_safety.db"
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
