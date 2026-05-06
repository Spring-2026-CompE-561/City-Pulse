from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from app.models import Event, User


async def get_next_user_id(db: AsyncSession) -> int:
    """Return the next user id (first user gets 0; then 1, 2, ...)."""
    max_id_result = await db.execute(select(func.max(User.id)))
    max_id = max_id_result.scalar()
    return 0 if max_id is None else max_id + 1


async def create_user(
    db: AsyncSession,
    *,
    id: int,
    name: str,
    email: str,
    password_hash: str,
    region_id: int | None,
) -> User:
    """Insert a new user row and return the ORM instance."""
    user = User(
        id=id,
        name=name,
        email=email,
        password_hash=password_hash,
        created_at=datetime.now(UTC),
        region_id=region_id,
    )
    db.add(user)
    await db.flush()
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Return a single user by email, or None."""
    result = await db.execute(select(User).where(col(User.email) == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """Return a single user by id, or None."""
    return await db.get(User, user_id)


async def list_users(db: AsyncSession, *, skip: int, limit: int) -> list[User]:
    """Return a slice of users."""
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


async def delete_user_and_events(db: AsyncSession, user_id: int) -> None:
    """Delete a user and their events (events first)."""
    exists_result = await db.execute(
        select(col(User.id)).where(col(User.id) == user_id)
    )
    if exists_result.scalar_one_or_none() is None:
        return
    await db.execute(
        Event.__table__.delete().where(Event.user_id == user_id)  # type: ignore[arg-type]
    )
    await db.flush()
    await db.execute(
        User.__table__.delete().where(User.id == user_id)  # type: ignore[arg-type]
    )
    await db.flush()

