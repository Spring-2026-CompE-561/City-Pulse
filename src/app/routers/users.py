"""User API: list, get, update (with password verification), delete.

Registration is via POST /api/auth/register.
"""

from fastapi import APIRouter, Depends, Path
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import bad_request, conflict, not_found, unauthorized
from app.auth import verify_password
from app.database import get_db
from app.models import Event, User
from app.region_map import city_location_to_region_id, region_id_to_city_location
from app.schemas import SuccessResponse, UserListResponse, UserRead, UserUpdate

router = APIRouter(prefix="/api/users", tags=["Users"])


def _user_to_read(user: User) -> UserRead:
    """Convert a `User` ORM object to the public `UserRead` schema."""
    return UserRead(
        id=user.id,
        name=user.name,
        email=user.email,
        city_location=region_id_to_city_location(user.region_id) if user.region_id is not None else None,
        created_at=user.created_at,
    )


@router.get("/", response_model=UserListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Get users in a single object: { users: [...], count: N }."""
    result = await db.execute(select(User).offset(skip).limit(limit))
    rows = list(result.scalars().all())
    return UserListResponse(users=[_user_to_read(u) for u in rows], count=len(rows))


@router.get("/{id}", response_model=UserRead)
async def get_user(
    id: int = Path(..., description="User ID (the 'id' field from the user list)"),
    db: AsyncSession = Depends(get_db),
):
    """Get one user by ID."""
    result = await db.execute(select(User).where(User.id == id))
    user = result.scalar_one_or_none()
    if not user:
        raise not_found("User not found")
    return _user_to_read(user)


@router.put("/{id}", response_model=SuccessResponse)
async def update_user(
    id: int = Path(..., description="User ID (the 'id' field from the user list)"),
    payload: UserUpdate = ...,
    db: AsyncSession = Depends(get_db),
):
    """Update user name/email/city_location. Requires current_password. city_location only 'san diego'."""
    result = await db.execute(select(User).where(User.id == id))
    user = result.scalar_one_or_none()
    if user is None:
        raise not_found("User not found")
    if not verify_password(payload.current_password, user.password_hash):
        raise unauthorized("Incorrect password")
    try:
        if payload.name is not None:
            user.name = payload.name
        if payload.email is not None:
            user.email = payload.email.strip().lower()
        if payload.city_location is not None:
            user.region_id = city_location_to_region_id(payload.city_location)
        await db.flush()
        return SuccessResponse()
    except ValueError as e:
        raise bad_request(str(e)) from e
    except IntegrityError as e:
        await db.rollback()
        msg = str(e.orig) if e.orig else str(e)
        if "Duplicate" in msg or "UNIQUE" in msg or "1062" in msg:
            raise conflict("Email already in use") from e
        raise bad_request("Invalid request") from e


@router.delete("/{id}", response_model=SuccessResponse)
async def delete_user(
    id: int = Path(..., description="User ID (the 'id' field from the user list)"),
    db: AsyncSession = Depends(get_db),
):
    """Delete a user by ID. Any events owned by the user are deleted first."""
    # Existence check using only id (avoids loading full row; works if schema is missing columns)
    exists = await db.execute(select(User.id).where(User.id == id))
    if exists.scalar_one_or_none() is None:
        raise not_found("User not found")
    await db.execute(delete(Event).where(Event.user_id == id))
    await db.flush()
    await db.execute(delete(User).where(User.id == id))
    await db.flush()
    return SuccessResponse()
