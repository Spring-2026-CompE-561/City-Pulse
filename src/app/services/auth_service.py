from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import (
    create_access_token,
    create_refresh_token,
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

