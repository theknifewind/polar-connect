"""AdminAccount and AdminSession ORM models."""

import secrets
from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from app.database import Base


class AdminAccount(Base):
    __tablename__ = "admin_accounts"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship(
        "AdminSession", back_populates="admin", cascade="all, delete-orphan"
    )


class AdminSession(Base):
    __tablename__ = "admin_sessions"

    session_id = Column(
        String,
        primary_key=True,
        default=lambda: secrets.token_hex(32),
    )
    admin_id = Column(
        String,
        ForeignKey("admin_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(
        DateTime,
        default=lambda: datetime.utcnow() + timedelta(days=7),
    )

    admin = relationship("AdminAccount", back_populates="sessions")
