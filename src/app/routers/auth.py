"""Register, login, and refresh tokens. Use access_token as Bearer for protected endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.models import User
from app.region_map import city_location_to_region_id, region_id_to_city_location
from app.schemas import LoginRequest, RefreshRequest, UserCreate, UserRead

router = APIRouter(prefix="/api/auth", tags=["Auth"])


def _user_to_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        name=user.name,
        email=user.email,
        city_location=region_id_to_city_location(user.region_id) if user.region_id is not None else None,
        created_at=user.created_at,
    )


def _is_duplicate_email_error(exc: IntegrityError) -> bool:
    msg = str(exc.orig) if exc.orig else str(exc)
    return "Duplicate" in msg or "UNIQUE" in msg or "unique" in msg or "1062" in msg


@router.post("/register")
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    **Register a new account.** Creates the user and returns access + refresh tokens.

    **Body:** name, email, password, city_location (only 'san diego').

    **Response:** `{ "access_token": "...", "refresh_token": "...", "token_type": "bearer" }`
    Use access_token as Bearer for /me and other protected endpoints. Use refresh_token at POST /api/auth/refresh to get a new access_token.
    """
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
            password_hash=hash_password(payload.password),
            region_id=region_id,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except IntegrityError as e:
        await db.rollback()
        if _is_duplicate_email_error(e):
            raise HTTPException(status_code=409, detail="Email already registered") from e
        raise HTTPException(status_code=400, detail="Invalid request") from e


@router.post("/login")
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    **Log in.** Returns access and refresh tokens.

    **Body:** email, password.

    **Response:** `{ "access_token": "...", "refresh_token": "...", "token_type": "bearer" }`
    Use access_token as Bearer for /me and protected endpoints. Use refresh_token at POST /api/auth/refresh to get a new access_token.
    """
    email = payload.email.strip().lower()
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
async def refresh(payload: RefreshRequest):
    """
    **Get a new access token** using a valid refresh token (from register or login).

    **Body:** `{ "refresh_token": "<your_refresh_token>" }`

    **Response:** `{ "access_token": "...", "refresh_token": "...", "token_type": "bearer" }`
    Use the new access_token as Bearer for protected endpoints.
    """
    data = decode_refresh_token(payload.refresh_token)
    if not data or "sub" not in data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user_id = int(data["sub"])
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id)
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserRead)
async def me(user: User | None = Depends(get_current_user)):
    """
    **Current user.** Requires a valid Bearer access token.

    Get a token via POST /api/auth/register or POST /api/auth/login, or refresh via POST /api/auth/refresh.
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _user_to_read(user)
