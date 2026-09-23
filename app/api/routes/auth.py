"""
Auth routes: create account, login, current user.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.db import get_db
from app.api.deps import get_current_user
from app.api.models import User
from app.api.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from app.api.security import create_access_token, hash_password, verify_password
from app.config.settings import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _token_response(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user.id),
        expires_in_minutes=settings.JWT_EXPIRE_MINUTES,
        user=UserOut.model_validate(user),
    )


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """New user creates an account and is signed in immediately."""
    existing = (
        db.query(User)
        .filter(
            or_(
                User.username == payload.username,
                User.email == payload.email.lower(),
            )
        )
        .first()
    )

    if existing is not None:
        field = (
            "username" if existing.username == payload.username else "email"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"That {field} is already registered.",
        )

    user = User(
        username=payload.username,
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        last_login_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return _token_response(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Existing user signs in with username-or-email plus password."""
    identifier = payload.identifier.strip()

    user = (
        db.query(User)
        .filter(
            or_(
                User.username == identifier,
                User.email == identifier.lower(),
            )
        )
        .first()
    )

    # Same message either way so the endpoint doesn't leak which
    # usernames exist.
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password.",
        )

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    return _token_response(user)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)
