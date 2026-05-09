import hashlib
import hmac
import secrets
from urllib.parse import urlencode

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.auth import (
    create_password_reset_token,
    create_access_token,
    create_refresh_token,
    decode_password_reset_token,
    hash_password,
    verify_password,
)
from app.models import User
from app.repository.region import resolve_region_id_for_city_location
from app.repository.user import (
    create_user,
    get_next_user_id,
    get_user_by_email,
)
from app.schemas import LoginRequest, UserCreate
from app.services.email_service import send_password_reset_email


def _build_reset_code_signature(email: str, access_code: str) -> str:
    data = f"{email}:{access_code}".encode()
    secret = settings.jwt_secret_key or ""
    return hmac.new(secret.encode(), data, hashlib.sha256).hexdigest()


def is_duplicate_email_error(exc: IntegrityError) -> bool:
    """Return True if the database error looks like a duplicate-email/UNIQUE constraint."""
    msg = str(exc.orig) if exc.orig else str(exc)
    return "Duplicate" in msg or "UNIQUE" in msg or "unique" in msg or "1062" in msg


def build_token_pair(user_id: int) -> dict:
    """Create and return an access/refresh token pair for a user id."""
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def require_user_id(user: User) -> int:
    """Return a non-null user id or raise if missing."""
    if user.id is None:
        raise ValueError("User id is missing")
    return user.id


async def register_user(db: AsyncSession, payload: UserCreate) -> dict:
    """Register a new user and return an access/refresh token pair."""
    email = payload.email.strip().lower()
    existing_user = await get_user_by_email(db, email)
    if existing_user is not None:
        raise ValueError("Email already registered")

    region_id = await resolve_region_id_for_city_location(
        db, city_location=payload.city_location
    )
    next_id = await get_next_user_id(db)
    user = await create_user(
        db,
        id=next_id,
        name=payload.name,
        email=email,
        password_hash=hash_password(payload.password),
        region_id=region_id,
    )
    return build_token_pair(require_user_id(user))


async def login_user(db: AsyncSession, payload: LoginRequest) -> dict | None:
    """Verify credentials and return token pair, or None if invalid."""
    email = payload.email.strip().lower()
    user = await get_user_by_email(db, email)
    if not user or not verify_password(payload.password, user.password_hash):
        return None
    return build_token_pair(require_user_id(user))


async def send_password_reset_instructions(db: AsyncSession, *, email: str) -> None:
    """
    Send password reset instructions (link + access code) if the account exists.

    This endpoint must be non-enumerating, so callers should always return
    a generic success message regardless of whether a user was found.
    """
    normalized_email = email.strip().lower()
    if not normalized_email:
        return
    user = await get_user_by_email(db, normalized_email)
    if user is None:
        return

    access_code = f"{secrets.randbelow(1_000_000):06d}"
    access_code_signature = _build_reset_code_signature(normalized_email, access_code)
    reset_token = create_password_reset_token(normalized_email, access_code_signature)

    query = urlencode(
        {
            "auth": "reset",
            "reset_token": reset_token,
            "reset_email": normalized_email,
        }
    )
    frontend_base_url = settings.frontend_base_url.rstrip("/")
    reset_link = f"{frontend_base_url}/?{query}"

    send_password_reset_email(
        recipient_email=normalized_email,
        reset_link=reset_link,
        access_code=access_code,
    )


async def reset_password_with_token(
    db: AsyncSession,
    *,
    token: str,
    access_code: str,
    new_password: str,
) -> bool:
    """
    Validate reset token + access code and update password hash.

    Returns False on invalid token/code/user and True when the password is updated.
    """
    payload = decode_password_reset_token(token)
    if payload is None:
        return False
    email = payload["sub"]
    expected_signature = payload["code_signature"]
    provided_signature = _build_reset_code_signature(email, access_code.strip())
    if not hmac.compare_digest(provided_signature, expected_signature):
        return False
    user = await get_user_by_email(db, email)
    if user is None:
        return False
    user.password_hash = hash_password(new_password)
    await db.flush()
    return True


def user_to_public(user: User) -> dict:
    """Map a User ORM instance into the public user dict."""
    # Import here to avoid circular dependencies.
    from app.region_map import region_id_to_city_location

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "city_location": region_id_to_city_location(user.region_id)
        if user.region_id is not None
        else None,
        "created_at": user.created_at,
    }

