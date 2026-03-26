"""
Authentication helpers: password hashing, access/refresh tokens,
and FastAPI dependencies.

What lives here
- Password hashing + verification helpers (`hash_password`, `verify_password`).
- In-memory access/refresh token stores and helpers to create/decode them.
- FastAPI dependency functions to retrieve the current user from a
  Bearer token.

Called by / import relationships
- `app.services.auth_service` imports:
  - `hash_password`, `verify_password` for credential handling
  - `create_access_token`, `create_refresh_token` for minting token pairs
- `app.routers.auth` imports:
  - `decode_refresh_token` for refresh endpoint
  - `get_current_user` for `/api/auth/me`
- Other routers can depend on `get_current_user_required` to protect endpoints.

Important behavior
- Tokens are stored in process memory. If the server restarts, all
  issued tokens become invalid.
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.config import settings
from app.database import get_db
from app.models import User

# In-memory token stores: token -> (user_id, expires_at).
# Trade-off: simple for demos; not suitable for multi-instance
# deployments or restarts.
_access_token_store: dict[str, tuple[int, datetime]] = {}
_refresh_token_store: dict[str, tuple[int, datetime]] = {}

# HTTPBearer gives Swagger a simple "Bearer token" paste field
# instead of the OAuth2 username/password/client form.
bearer_scheme = HTTPBearer(auto_error=False)


def _hash_password(password: str) -> str:
    """
    Return a SHA-256 hash for the given plain-text password.

    Called by
    - `hash_password` and `verify_password` in this module.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain: str, password_hash: str) -> bool:
    """
    Check whether a plain-text password matches the stored hash.

    Called by
    - `app.services.auth_service.login_user`
    - `app.routers.users.update_user` (verifies `current_password`
      before updates)
    """
    return _hash_password(plain) == password_hash


def hash_password(plain: str) -> str:
    """
    Hash a new user password for storage in the database.

    Called by
    - `app.services.auth_service.register_user` when creating a new user.
    """
    return _hash_password(plain)


def create_access_token(user_id: int) -> str:
    """
    Create and store a new short-lived access token for `user_id`.

    Called by
    - `app.services.auth_service.build_token_pair`

    Returns
    - A random URL-safe string that the client sends as a Bearer token.
    """
    # Random, URL-safe token string.
    token = secrets.token_urlsafe(32)
    # Compute expiration using configured TTL.
    expires = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    # Persist in memory for later validation/lookup.
    _access_token_store[token] = (user_id, expires)
    return token


def create_refresh_token(user_id: int) -> str:
    """
    Create and store a new long-lived refresh token for `user_id`.

    Called by
    - `app.services.auth_service.build_token_pair`
    """
    token = secrets.token_urlsafe(32)
    expires = datetime.now(UTC) + timedelta(
        days=settings.refresh_token_expire_days
    )
    _refresh_token_store[token] = (user_id, expires)
    return token


def decode_access_token(token: str) -> dict | None:
    """
    Validate an access token and return its payload, or None.

    Returns
    - `{"sub": "<user_id_as_str>"}` if token exists and is not expired.
    - None if token is missing, unknown, or expired.

    Called by
    - `get_current_user` dependency below.
    """
    if not token or token not in _access_token_store:
        return None
    user_id, expires = _access_token_store[token]
    if datetime.now(UTC) >= expires:
        # Clean up expired token to prevent unbounded growth.
        del _access_token_store[token]
        return None
    return {"sub": str(user_id)}


def decode_refresh_token(token: str) -> dict | None:
    """
    Validate a refresh token and return its payload, or None.

    Called by
    - `app.routers.auth.refresh` to mint a new access token.
    """
    if not token or token not in _refresh_token_store:
        return None
    user_id, expires = _refresh_token_store[token]
    if datetime.now(UTC) >= expires:
        # Clean up expired token to prevent unbounded growth.
        del _refresh_token_store[token]
        return None
    return {"sub": str(user_id)}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """
    FastAPI dependency: resolve the current user from a Bearer access token.

    Parameters
    - `credentials`: automatically extracted from the Authorization header
      by `bearer_scheme`.
    - `db`: an async DB session provided by `app.database.get_db`.

    Returns
    - A `User` ORM instance if token is valid and user exists.
    - None if missing/invalid/expired token or user not found.

    Called by
    - `app.routers.auth.me` (and potentially other protected endpoints).
    """
    if not credentials:
        return None
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    try:
        user_id = int(payload["sub"])
    except (ValueError, TypeError):
        return None
    result = await db.execute(select(User).where(col(User.id) == user_id))
    return result.scalar_one_or_none()


async def get_current_user_required(
    user: User | None = Depends(get_current_user),
) -> User:
    """
    FastAPI dependency: like `get_current_user` but enforces authentication.

    Called by
    - Any router endpoint that wants to require a Bearer token.
      (Currently available for use.)
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
