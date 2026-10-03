from __future__ import annotations
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from app.config import settings, ROOT_DIR
from app.database.models import Base


def _normalize_sqlite_url(url: str) -> str:
    if not url.startswith("sqlite:///"):
        return url
    raw = url.replace("sqlite:///", "", 1)
    p = Path(raw)
    if not p.is_absolute():
        p = ROOT_DIR / raw
    p.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{p.as_posix()}"


DATABASE_URL = _normalize_sqlite_url(settings.database_url)
engine = create_engine(
    DATABASE_URL,
    future=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def _lightweight_sqlite_migrations() -> None:
    """Add backward-compatible columns for users opening an older local database."""
    if not DATABASE_URL.startswith("sqlite"):
        return
    inspector = inspect(engine)
    if "followups" not in inspector.get_table_names():
        return
    columns = {c["name"] for c in inspector.get_columns("followups")}
    with engine.begin() as conn:
        if "scheduled_for" not in columns:
            conn.execute(text("ALTER TABLE followups ADD COLUMN scheduled_for DATETIME"))
        if "completed_at" not in columns:
            conn.execute(text("ALTER TABLE followups ADD COLUMN completed_at DATETIME"))


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _lightweight_sqlite_migrations()


def get_session():
    init_db()
    return SessionLocal()
