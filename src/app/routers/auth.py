"""Register, login, and refresh tokens. Use access_token as Bearer for protected endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import decode_refresh_token, get_current_user, get_current_user_required, verify_password
from app.database import get_db
from app.exceptions import bad_request, conflict, unauthorized
from app.models import User
from app.repositories.user_repository import delete_user_and_events
from app.schemas import LoginRequest, RefreshRequest, SuccessResponse, UserCreate, UserDeleteBody, UserRead
from app.services.auth_service import (
    build_token_pair,
    is_duplicate_email_error,
    login_user,
    register_user,
    user_to_public,
)

router = APIRouter(prefix="/api/auth", tags=["Auth"])


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
        return await register_user(db, payload)
    except ValueError as e:
        if str(e) == "Email already registered":
            raise conflict("Email already registered") from e
        raise bad_request(str(e)) from e
    except IntegrityError as e:
        await db.rollback()
        if is_duplicate_email_error(e):
            raise conflict("Email already registered") from e
        raise bad_request("Invalid request") from e


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
    token_pair = await login_user(db, payload)
    if token_pair is None:
        raise unauthorized("Incorrect email or password")
    return token_pair


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
        raise unauthorized("Invalid or expired refresh token")
    try:
        user_id = int(data["sub"])
    except (ValueError, TypeError):
        raise unauthorized("Invalid refresh token") from None
    return build_token_pair(user_id)


@router.get("/me", response_model=UserRead)
async def me(user=Depends(get_current_user)):
    """
    **Current user.** Requires a valid Bearer access token.

    Get a token via POST /api/auth/register or POST /api/auth/login, or refresh via POST /api/auth/refresh.
    """
    if user is None:
        raise unauthorized("Not authenticated")
    return UserRead(**user_to_public(user))


@router.delete("/me", response_model=SuccessResponse)
async def delete_me(
    payload: UserDeleteBody = ...,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
):
    """
    **Delete your account.** Requires Bearer auth and password confirmation.

    All events owned by the user are removed as well.

    **Body:** `{ "password": "your_current_password" }`
    """
    if not verify_password(payload.password, current_user.password_hash):
        raise unauthorized("Incorrect password")
    await delete_user_and_events(db, current_user.id)
    return SuccessResponse()
