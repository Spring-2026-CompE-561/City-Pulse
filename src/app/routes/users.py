"""User API: list, get, update (with password verification).

Registration is via POST /api/auth/register. Deletion is via DELETE /api/auth/me.
"""

from fastapi import APIRouter, Depends, Path
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_password
from app.database import get_db
from app.exceptions import bad_request, conflict, not_found, unauthorized
from app.models import User
from app.region_map import region_id_to_city_location
from app.repository.region import resolve_region_id_for_city_location
from app.repository.user import get_user_by_id
from app.repository.user import (
    list_users as list_user_rows,
)
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
    rows = await list_user_rows(db, skip=skip, limit=limit)
    return UserListResponse(users=[_user_to_read(u) for u in rows], count=len(rows))


@router.get("/{id}", response_model=UserRead)
async def get_user(
    id: int = Path(..., description="User ID (the 'id' field from the user list)"),
    db: AsyncSession = Depends(get_db),
):
    """Get one user by ID."""
    user = await get_user_by_id(db, id)
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
    user = await get_user_by_id(db, id)
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
            user.region_id = await resolve_region_id_for_city_location(
                db, city_location=payload.city_location
            )
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

