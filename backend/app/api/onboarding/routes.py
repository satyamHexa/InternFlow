from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.repositories.referral_repository import ReferralRepository
from app.repositories.onboarding_repository import OnboardingRepository
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.onboarding import (
    CompleteOnboardingTaskRequest,
    CreateOnboardingTaskRequest,
    OnboardingTaskResponse,
    UpdateOnboardingTaskRequest,
)
from app.api.auth.dependencies import CurrentUser, require_roles

router = APIRouter()
_referral_repo = ReferralRepository()
_onboarding_repo = OnboardingRepository()
HR_ROLES = require_roles(UserRole.HR, UserRole.PROGRAM_OWNER)


# ── NDA ────────────────────────────────────────────────────────────────────

class SignNDARequest(BaseModel):
    signature_data: str


class NDAResponse(BaseModel):
    referral_id: uuid.UUID
    signed: bool
    blob_url: str | None


@router.post("/{referral_id}/nda/generate", response_model=NDAResponse)
async def generate_nda(
    referral_id: uuid.UUID,
    current_user: Annotated[object, Depends(HR_ROLES)],
    db: AsyncSession = Depends(get_db),
) -> NDAResponse:
    referral = await _referral_repo.get(referral_id, db)
    if referral is None:
        raise NotFoundException("Referral")
    from app.services.nda_service import nda_service

    result = await nda_service.generate_nda(
        str(referral_id), referral.candidate_name
    )
    return NDAResponse(
        referral_id=referral_id,
        signed=False,
        blob_url=result.get("blob_url"),
    )


@router.post("/{referral_id}/nda/sign", response_model=NDAResponse)
async def sign_nda(
    referral_id: uuid.UUID,
    payload: SignNDARequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> NDAResponse:
    referral = await _referral_repo.get(referral_id, db)
    if referral is None:
        raise NotFoundException("Referral")
    from app.services.nda_service import nda_service

    result = await nda_service.sign_nda(str(referral_id), payload.signature_data)
    await _referral_repo.update(referral_id, {"status": "nda_signed"}, db)
    return NDAResponse(referral_id=referral_id, signed=True, blob_url=None)


# ── Onboarding Tasks ────────────────────────────────────────────────────────

@router.get(
    "/{referral_id}/tasks",
    response_model=list[OnboardingTaskResponse],
)
async def list_onboarding_tasks(
    referral_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    status_filter: str | None = Query(default=None, alias="status"),
    category: str | None = Query(default=None),
) -> list[OnboardingTaskResponse]:
    referral = await _referral_repo.get(referral_id, db)
    if referral is None:
        raise NotFoundException("Referral")
    tasks = await _onboarding_repo.get_by_referral(
        referral_id, db,
        status_filter=status_filter,
        category_filter=category,
    )
    return [OnboardingTaskResponse.model_validate(t) for t in tasks]


@router.post(
    "/{referral_id}/tasks",
    response_model=OnboardingTaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_onboarding_task(
    referral_id: uuid.UUID,
    payload: CreateOnboardingTaskRequest,
    current_user: Annotated[object, Depends(HR_ROLES)],
    db: AsyncSession = Depends(get_db),
) -> OnboardingTaskResponse:
    referral = await _referral_repo.get(referral_id, db)
    if referral is None:
        raise NotFoundException("Referral")
    task = await _onboarding_repo.create(
        {
            "referral_id": referral_id,
            "title": payload.title,
            "description": payload.description,
            "category": payload.category,
            "assigned_to": payload.assigned_to,
            "due_date": payload.due_date,
            "status": "pending",
        },
        db,
    )
    return OnboardingTaskResponse.model_validate(task)


@router.get(
    "/tasks/my",
    response_model=list[OnboardingTaskResponse],
)
async def list_my_onboarding_tasks(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> list[OnboardingTaskResponse]:
    tasks = await _onboarding_repo.get_assigned_to(current_user.id, db)
    return [OnboardingTaskResponse.model_validate(t) for t in tasks]


@router.get(
    "/tasks/{task_id}",
    response_model=OnboardingTaskResponse,
)
async def get_onboarding_task(
    task_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> OnboardingTaskResponse:
    task = await _onboarding_repo.get(task_id, db)
    if task is None:
        raise NotFoundException("OnboardingTask")
    return OnboardingTaskResponse.model_validate(task)


@router.put(
    "/tasks/{task_id}",
    response_model=OnboardingTaskResponse,
)
async def update_onboarding_task(
    task_id: uuid.UUID,
    payload: UpdateOnboardingTaskRequest,
    current_user: Annotated[object, Depends(HR_ROLES)],
    db: AsyncSession = Depends(get_db),
) -> OnboardingTaskResponse:
    task = await _onboarding_repo.get(task_id, db)
    if task is None:
        raise NotFoundException("OnboardingTask")
    data = payload.model_dump(exclude_none=True)
    updated = await _onboarding_repo.update(task_id, data, db)
    return OnboardingTaskResponse.model_validate(updated)


@router.post(
    "/tasks/{task_id}/complete",
    response_model=OnboardingTaskResponse,
)
async def complete_onboarding_task(
    task_id: uuid.UUID,
    payload: CompleteOnboardingTaskRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> OnboardingTaskResponse:
    task = await _onboarding_repo.get(task_id, db)
    if task is None:
        raise NotFoundException("OnboardingTask")
    updated = await _onboarding_repo.update(
        task_id,
        {
            "status": "completed",
            "completed_at": datetime.now(timezone.utc),
            "notes": payload.notes,
        },
        db,
    )
    return OnboardingTaskResponse.model_validate(updated)


@router.delete(
    "/tasks/{task_id}",
    response_model=MessageResponse,
)
async def delete_onboarding_task(
    task_id: uuid.UUID,
    current_user: Annotated[object, Depends(HR_ROLES)],
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Soft-delete an onboarding task."""
    deleted = await _onboarding_repo.delete(task_id, db)
    if not deleted:
        raise NotFoundException("OnboardingTask")
    return MessageResponse(message="Onboarding task deleted successfully")
