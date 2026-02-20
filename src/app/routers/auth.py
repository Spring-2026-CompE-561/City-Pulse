"""Login with email and password (same as user identity). Use access_token in Authorization: Bearer."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, get_current_user, verify_password
from app.database import get_db
from app.models import User
from app.region_map import region_id_to_city_location
from app.schemas import LoginRequest, UserRead

router = APIRouter(prefix="/api/auth", tags=["Auth"])


def _user_to_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        name=user.name,
        email=user.email,
        city_location=region_id_to_city_location(user.region_id) if user.region_id is not None else None,
        created_at=user.created_at,
    )


@router.post("/login")
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    **Get authentication (Bearer) token for a user.**

    **Parameters (request body):**
    - **email** (required): The user's email (same as when the account was created).
    - **password** (required): The user's current password.

    **Response:** `{ "access_token": "<token>", "token_type": "bearer" }`  
    Use `access_token` as the Bearer token: in **Authorize** enter `Bearer <access_token>`, or send header  
    `Authorization: Bearer <access_token>` for GET /api/auth/me and other protected endpoints.
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
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
async def me(user: User | None = Depends(get_current_user)):
    """
    **Current user.** Requires a valid Bearer token.

    **How to get the Bearer token:** Call **POST /api/auth/login** with body:
    `{ "email": "<user email>", "password": "<user password>" }`.
    Use the returned **access_token** in the **Authorize** button (enter `Bearer <access_token>`) or in the  
    `Authorization: Bearer <access_token>` header.
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _user_to_read(user)
