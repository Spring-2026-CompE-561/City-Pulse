"""Auth: password hashing, access/refresh tokens. Register and login return tokens; refresh endpoint issues new access token."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import User

# In-memory token stores: token -> (user_id, expires_at). Tokens are lost on server restart.
_access_token_store: dict[str, tuple[int, datetime]] = {}
_refresh_token_store: dict[str, tuple[int, datetime]] = {}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)


def _hash_password(password: str) -> str:
    """Return a SHA-256 hash for the given plain-text password."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain: str, password_hash: str) -> bool:
    """Check whether a plain-text password matches the stored hash."""
    return _hash_password(plain) == password_hash


def hash_password(plain: str) -> str:
    """Hash a new user password for storage in the database."""
    return _hash_password(plain)


def create_access_token(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    expires = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    _access_token_store[token] = (user_id, expires)
    return token


def create_refresh_token(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    expires = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    _refresh_token_store[token] = (user_id, expires)
    return token


def decode_access_token(token: str) -> dict | None:
    """Return {"sub": user_id} if token valid and not expired, else None."""
    if not token or token not in _access_token_store:
        return None
    user_id, expires = _access_token_store[token]
    if datetime.now(UTC) >= expires:
        del _access_token_store[token]
        return None
    return {"sub": str(user_id)}


def decode_refresh_token(token: str) -> dict | None:
    """Return {"sub": user_id} if refresh token valid and not expired, else None."""
    if not token or token not in _refresh_token_store:
        return None
    user_id, expires = _refresh_token_store[token]
    if datetime.now(UTC) >= expires:
        del _refresh_token_store[token]
        return None
    return {"sub": str(user_id)}


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Dependency: User from Bearer token, or None."""
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    try:
        user_id = int(payload["sub"])
    except (ValueError, TypeError):
        return None
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_current_user_required(user: User | None = Depends(get_current_user)) -> User:
    """Dependency: User or 401."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
