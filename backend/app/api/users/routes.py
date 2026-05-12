from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.core.database import get_db
from app.core.exceptions import ConflictException, NotFoundException
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.api.auth.dependencies import CurrentUser, require_roles

router = APIRouter()
_user_repo = UserRepository()

HR_ONLY = require_roles(UserRole.HR, UserRole.PROGRAM_OWNER)


@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    current_user: Annotated[object, Depends(HR_ONLY)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    role: str | None = Query(default=None),
    department: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
) -> PaginatedResponse[UserResponse]:
    filters = []
    if role:
        filters.append(User.role == role)
    if department:
        filters.append(User.department == department)
    if is_active is not None:
        filters.append(User.is_active == is_active)

    items, total = await _user_repo.list(db, filters=filters, offset=(page - 1) * page_size, limit=page_size)
    return PaginatedResponse.create(
        items=[UserResponse.model_validate(u) for u in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    current_user: Annotated[object, Depends(HR_ONLY)],
    db: AsyncSession = Depends(get_db),
) -> User:
    existing = await _user_repo.get_by_email(payload.email, db)
    if existing:
        raise ConflictException("A user with this email already exists")
    from app.core.security import hash_password

    user = await _user_repo.create(
        {
            "name": payload.name,
            "email": payload.email.lower(),
            "role": payload.role.value,
            "department": payload.department,
            "password_hash": hash_password(payload.password),
            "is_active": True,
        },
        db,
    )
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: CurrentUser) -> User:
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    current_user: Annotated[object, Depends(HR_ONLY)],
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _user_repo.get(user_id, db)
    if user is None:
        raise NotFoundException("User")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    current_user: Annotated[object, Depends(HR_ONLY)],
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _user_repo.get(user_id, db)
    if user is None:
        raise NotFoundException("User")
    data = payload.model_dump(exclude_none=True)
    if "role" in data:
        data["role"] = data["role"].value
    updated = await _user_repo.update(user_id, data, db)
    return updated


@router.post("/{user_id}/deactivate", response_model=MessageResponse)
async def deactivate_user(
    user_id: uuid.UUID,
    current_user: Annotated[object, Depends(HR_ONLY)],
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    user = await _user_repo.get(user_id, db)
    if user is None:
        raise NotFoundException("User")
    await _user_repo.update(user_id, {"is_active": False}, db)
    return MessageResponse(message="User deactivated successfully")


@router.post("/{user_id}/reactivate", response_model=MessageResponse)
async def reactivate_user(
    user_id: uuid.UUID,
    current_user: Annotated[object, Depends(HR_ONLY)],
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    user = await _user_repo.get(user_id, db)
    if user is None:
        raise NotFoundException("User")
    await _user_repo.update(user_id, {"is_active": True}, db)
    return MessageResponse(message="User reactivated successfully")


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: uuid.UUID,
    current_user: Annotated[object, Depends(HR_ONLY)],
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Soft-delete a user. The record remains in the DB with deleted_at set."""
    deleted = await _user_repo.delete(user_id, db)
    if not deleted:
        raise NotFoundException("User")
    return MessageResponse(message="User deleted successfully")
