"""SQLAlchemy engine, session maker, base model, and FastAPI dependency."""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

# Fallback to local SQLite if DATABASE_URL is empty
_db_url = settings.DATABASE_URL or "sqlite:///./polar_connect.db"

# SQLite needs check_same_thread=False for FastAPI's threaded access
connect_args: dict = {}
engine_kwargs: dict = {
    "echo": False,
    "pool_pre_ping": True,  # auto-heal stale connections
}

if _db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # PostgreSQL pool settings for production-readiness
    engine_kwargs.update({
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
        "pool_recycle": 1800,  # recycle connections after 30 min
    })

logger.info("Database: %s", _db_url.split("@")[-1] if "@" in _db_url else _db_url)

engine = create_engine(_db_url, connect_args=connect_args, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


def get_db():
    """FastAPI dependency — yields a scoped DB session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Import all models and create tables if they don't exist."""
    import app.models.admin       # noqa: F401
    import app.models.repository  # noqa: F401
    import app.models.station     # noqa: F401
    import app.models.learning    # noqa: F401
    import app.models.media       # noqa: F401
    import app.models.studio      # noqa: F401
    Base.metadata.create_all(bind=engine)
