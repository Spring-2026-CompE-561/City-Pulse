"""User API: list, get, create, update (with password verification), delete. City location = region (san diego only)."""

import hashlib

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Event, User
from app.region_map import city_location_to_region_id, region_id_to_city_location
from app.schemas import SuccessResponse, UserCreate, UserListResponse, UserRead, UserUpdate

router = APIRouter(prefix="/api/users", tags=["Users"])


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _verify_password(password: str, password_hash: str) -> bool:
    return _hash_password(password) == password_hash


def _user_to_read(user: User) -> UserRead:
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
        raise HTTPException(status_code=404, detail="User not found")
    return _user_to_read(user)


@router.post("/", response_model=UserRead, status_code=201)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user. First user gets id=0, then 1, 2, ... Body: name, email, password, city_location (only 'san diego')."""
    try:
        region_id = city_location_to_region_id(payload.city_location)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    try:
        max_id_result = await db.execute(select(func.max(User.id)))
        max_id = max_id_result.scalar()
        next_id = 0 if max_id is None else max_id + 1
        user = User(
            id=next_id,
            name=payload.name,
            email=payload.email.strip().lower(),
            password_hash=_hash_password(payload.password),
            region_id=region_id,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return _user_to_read(user)
    except IntegrityError as e:
        await db.rollback()
        if "UNIQUE constraint failed: users.email" in str(e.orig):
            raise HTTPException(status_code=409, detail="Email already registered") from e
        raise HTTPException(status_code=400, detail="Invalid request") from e


@router.put("/{id}", response_model=SuccessResponse)
async def update_user(
    id: int = Path(..., description="User ID (the 'id' field from the user list)"),
    payload: UserUpdate = ...,
    db: AsyncSession = Depends(get_db),
):
    """Update user name/email/city_location. Requires current_password. city_location only 'san diego'."""
    result = await db.execute(select(User).where(User.id == id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not _verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect password")
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
        raise HTTPException(status_code=400, detail=str(e)) from e
    except IntegrityError as e:
        await db.rollback()
        if "UNIQUE constraint failed: users.email" in str(e.orig):
            raise HTTPException(status_code=409, detail="Email already in use") from e
        raise HTTPException(status_code=400, detail="Invalid request") from e


@router.delete("/{id}", response_model=SuccessResponse)
async def delete_user(
    id: int = Path(..., description="User ID (the 'id' field from the user list)"),
    db: AsyncSession = Depends(get_db),
):
    """Delete a user by ID. Any events owned by the user are deleted first."""
    # Existence check using only id (avoids loading full row; works if schema is missing columns)
    exists = await db.execute(select(User.id).where(User.id == id))
    if exists.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="User not found")
    await db.execute(delete(Event).where(Event.user_id == id))
    await db.flush()
    await db.execute(delete(User).where(User.id == id))
    await db.flush()
    return SuccessResponse()
