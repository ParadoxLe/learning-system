from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from backend.config import DATABASE_URL
import os

# Resolve data directory relative to this file's location
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_BACKEND_DIR)
_DATA_DIR = os.path.join(_PROJECT_DIR, "data")
os.makedirs(_DATA_DIR, exist_ok=True)

_DB_PATH = os.path.join(_DATA_DIR, "learning_system.db")
_DATABASE_URL = f"sqlite:///{_DB_PATH}"

engine = create_engine(_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency injection for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables and run migrations."""
    Base.metadata.create_all(bind=engine)
    _migrate()


def _migrate():
    """Add missing columns to existing tables (idempotent)."""
    import sqlite3
    try:
        with engine.connect() as conn:
            # Add avatar column if missing
            cols = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(users);")]
            if "avatar" not in cols:
                conn.exec_driver_sql("ALTER TABLE users ADD COLUMN avatar VARCHAR(512);")
                conn.commit()
    except Exception:
        pass  # Not SQLite or already handled
