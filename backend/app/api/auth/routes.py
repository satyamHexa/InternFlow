from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.schemas.user import UserCreate, UserResponse
from app.api.auth.dependencies import CurrentUser

import uuid

router = APIRouter()
_user_repo = UserRepository()


# ──────────────────────────────────────────────────────────────
# POST /login
# ──────────────────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    user = await _user_repo.get_by_email(credentials.email, db)
    if user is None or not verify_password(credentials.password, user.password_hash):
        raise UnauthorizedException("Invalid email or password")
    if not user.is_active:
        raise UnauthorizedException("Account is inactive")

    token_data = {"sub": str(user.id), "role": user.role, "email": user.email}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ──────────────────────────────────────────────────────────────
# POST /register
# ──────────────────────────────────────────────────────────────
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    existing = await _user_repo.get_by_email(user_in.email, db)
    if existing:
        raise ConflictException("An account with this email already exists")

    user = await _user_repo.create(
        {
            "name": user_in.name,
            "email": user_in.email,
            "role": user_in.role.value,
            "department": user_in.department,
            "password_hash": hash_password(user_in.password),
            "is_active": True,
        },
        db,
    )
    return user


# ──────────────────────────────────────────────────────────────
# POST /refresh
# ──────────────────────────────────────────────────────────────
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload_in: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    payload = verify_token(payload_in.refresh_token, expected_type="refresh")
    sub = payload.get("sub")
    if sub is None:
        raise UnauthorizedException()

    user = await _user_repo.get(uuid.UUID(sub), db)
    if user is None or not user.is_active:
        raise UnauthorizedException("User not found or inactive")

    token_data = {"sub": str(user.id), "role": user.role, "email": user.email}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ──────────────────────────────────────────────────────────────
# GET /profile
# ──────────────────────────────────────────────────────────────
@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: CurrentUser) -> User:
    return current_user


# ──────────────────────────────────────────────────────────────
# POST /change-password
# ──────────────────────────────────────────────────────────────
@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    if not verify_password(payload.current_password, current_user.password_hash):
        raise UnauthorizedException("Current password is incorrect")
    await _user_repo.update(
        current_user.id,
        {"password_hash": hash_password(payload.new_password)},
        db,
    )


# ──────────────────────────────────────────────────────────────
# POST /logout
# JWT is stateless. Client must discard the token.
# For full revocation, add the jti to a Redis blocklist here.
# ──────────────────────────────────────────────────────────────
@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: CurrentUser) -> None:
    pass
