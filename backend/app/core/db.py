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
    # Look for existing road_safety.db in candidate locations
    current_dir = os.path.dirname(os.path.abspath(__file__))  # backend/app/core
    backend_dir = os.path.dirname(os.path.dirname(current_dir))  # backend
    project_root = os.path.dirname(backend_dir)  # project root

    candidates = [
        os.path.join(backend_dir, "road_safety.db"),
        os.path.join(project_root, "road_safety.db"),
        os.path.join(os.getcwd(), "road_safety.db"),
        os.path.join(os.getcwd(), "backend", "road_safety.db"),
    ]
    sqlite_file = candidates[0]
    for c in candidates:
        if os.path.isfile(c) and os.path.getsize(c) > 1000:
            sqlite_file = c
            break

    sqlite_file = os.path.abspath(sqlite_file).replace("\\", "/")
    SQLITE_URL = f"sqlite:///{sqlite_file}"
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
