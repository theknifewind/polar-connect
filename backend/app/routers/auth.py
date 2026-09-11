"""/api/auth — login, logout, session status."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import create_session, get_current_admin, hash_password, verify_password
from app.database import get_db
from app.models.admin import AdminAccount, AdminSession

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ── Request / Response DTOs (local to this router) ──────────

class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    message: str
    email: str


class MeResponse(BaseModel):
    id: str
    email: str


# ── Endpoints ────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, response: Response, db: Session = Depends(get_db)):
    admin = db.query(AdminAccount).filter(AdminAccount.email == body.email).first()
    if not admin or not verify_password(body.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    session = create_session(db, admin.id)
    response.set_cookie(
        key="polar_session",
        value=session.session_id,
        httponly=True,
        samesite="lax",
        secure=False,       # Set True in production with HTTPS
        max_age=7 * 24 * 60 * 60,
        path="/",
    )
    return LoginResponse(message="Logged in successfully", email=admin.email)


@router.post("/logout")
def logout(
    response: Response,
    admin: AdminAccount = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    db.query(AdminSession).filter(AdminSession.admin_id == admin.id).delete()
    db.commit()
    response.delete_cookie("polar_session", path="/")
    return {"message": "Logged out"}


@router.get("/me", response_model=MeResponse)
def get_me(admin: AdminAccount = Depends(get_current_admin)):
    return MeResponse(id=admin.id, email=admin.email)
