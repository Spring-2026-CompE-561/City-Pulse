"""
Authentication helpers: password hashing, JWT access/refresh tokens,
and FastAPI dependencies.

What lives here
- Password hashing + verification helpers (`hash_password`, `verify_password`).
- JWT access/refresh token helpers to create/decode token pairs.
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
- Tokens are signed JWTs. Validation checks signature, expiry, and token type.
"""

import hashlib
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.config import settings
from app.database import get_db
from app.models import User

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
    Create a signed short-lived JWT access token for `user_id`.

    Called by
    - `app.services.auth_service.build_token_pair`

    Returns
    - A signed JWT string that the client sends as a Bearer token.
    """
    now = datetime.now(UTC)
    expires = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(user_id: int) -> str:
    """
    Create a signed long-lived JWT refresh token for `user_id`.

    Called by
    - `app.services.auth_service.build_token_pair`
    """
    now = datetime.now(UTC)
    expires = now + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict | None:
    """
    Validate an access token and return its payload, or None.

    Returns
    - `{"sub": "<user_id_as_str>"}` if token is valid and not expired.
    - None if token is missing, invalid, wrong type, or expired.

    Called by
    - `get_current_user` dependency below.
    """
    if not token:
        return None
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.InvalidTokenError:
        return None
    if payload.get("type") != "access":
        return None
    if "sub" not in payload:
        return None
    return {"sub": str(payload["sub"])}


def decode_refresh_token(token: str) -> dict | None:
    """
    Validate a refresh token and return its payload, or None.

    Called by
    - `app.routers.auth.refresh` to mint a new access token.
    """
    if not token:
        return None
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.InvalidTokenError:
        return None
    if payload.get("type") != "refresh":
        return None
    if "sub" not in payload:
        return None
    return {"sub": str(payload["sub"])}


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


def require_ingest_api_key(x_ingest_key: str | None = Header(default=None)) -> None:
    """
    Require a configured ingest API key for ingestion/admin endpoints.
    """
    if not settings.ingest_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ingestion key is not configured",
        )
    if x_ingest_key != settings.ingest_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ingestion key",
        )
