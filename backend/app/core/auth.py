"""Cookie-based session authentication, password hashing (bcrypt)."""

import secrets
from datetime import datetime, timedelta

import bcrypt
from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin import AdminAccount, AdminSession


def hash_password(password: str) -> str:
    """Hash a plain-text password with bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_session(db: Session, admin_id: str) -> AdminSession:
    """Create a new session row and return it."""
    session = AdminSession(
        session_id=secrets.token_hex(32),
        admin_id=admin_id,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_current_admin(
    polar_session: str | None = Cookie(None, alias="polar_session"),
    db: Session = Depends(get_db),
) -> AdminAccount:
    """FastAPI dependency — validates the session cookie and returns the admin.

    Raises 401 if the cookie is missing, expired, or invalid.
    """
    if not polar_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    session = (
        db.query(AdminSession)
        .filter(
            AdminSession.session_id == polar_session,
            AdminSession.expires_at > datetime.utcnow(),
        )
        .first()
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid",
        )

    admin = db.query(AdminAccount).filter(AdminAccount.id == session.admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin account not found",
        )

    return admin
