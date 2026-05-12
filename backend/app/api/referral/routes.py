from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.core.database import get_db
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.referral import Referral
from app.repositories.referral_repository import ReferralRepository
from app.schemas.common import PaginatedResponse
from app.schemas.referral import (
    CreateReferralRequest,
    ReferralDetailResponse,
    ReferralResponse,
    RejectReferralRequest,
    ResumeUploadResponse,
    UpdateReferralRequest,
)
from app.api.auth.dependencies import CurrentUser, require_roles

router = APIRouter()
_referral_repo = ReferralRepository()

HR_ROLES = require_roles(UserRole.HR, UserRole.PROGRAM_OWNER)


@router.post(
    "/",
    response_model=ReferralResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_referral(
    payload: CreateReferralRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Referral:
    # Duplicate check
    duplicate = await _referral_repo.find_duplicate(payload.candidate_email, db)
    is_dup = duplicate is not None

    referral = await _referral_repo.create(
        {
            "candidate_name": payload.candidate_name,
            "candidate_email": payload.candidate_email,
            "candidate_phone": payload.candidate_phone,
            "department": payload.department,
            "referrer_id": current_user.id,
            "mentor_id": payload.mentor_id,
            "status": "submitted",
            "is_duplicate": is_dup,
            "duplicate_of_id": duplicate.id if is_dup else None,
        },
        db,
    )
    return referral


@router.get("/", response_model=PaginatedResponse[ReferralResponse])
async def list_referrals(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_filter: str | None = Query(default=None, alias="status"),
    department: str | None = Query(default=None),
) -> PaginatedResponse[ReferralResponse]:
    filters = []
    if status_filter:
        filters.append(Referral.status == status_filter)
    if department:
        filters.append(Referral.department == department)

    # Employees can only see their own referrals
    if current_user.role == UserRole.EMPLOYEE.value:
        filters.append(Referral.referrer_id == current_user.id)

    items, total = await _referral_repo.list(
        db,
        filters=filters,
        offset=(page - 1) * page_size,
        limit=page_size,
    )
    return PaginatedResponse.create(
        items=[ReferralResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{referral_id}", response_model=ReferralDetailResponse)
async def get_referral(
    referral_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Referral:
    referral = await _referral_repo.get(referral_id, db)
    if referral is None:
        raise NotFoundException("Referral")
    if (
        current_user.role == UserRole.EMPLOYEE.value
        and referral.referrer_id != current_user.id
    ):
        raise ForbiddenException()
    return referral


@router.put("/{referral_id}", response_model=ReferralResponse)
async def update_referral(
    referral_id: uuid.UUID,
    payload: UpdateReferralRequest,
    current_user: Annotated[object, Depends(HR_ROLES)],
    db: AsyncSession = Depends(get_db),
) -> Referral:
    referral = await _referral_repo.get(referral_id, db)
    if referral is None:
        raise NotFoundException("Referral")
    data = payload.model_dump(exclude_none=True)
    if "status" in data:
        data["status"] = data["status"].value
    updated = await _referral_repo.update(referral_id, data, db)
    return updated


@router.post("/{referral_id}/approve", response_model=ReferralResponse)
async def approve_referral(
    referral_id: uuid.UUID,
    current_user: Annotated[object, Depends(HR_ROLES)],
    db: AsyncSession = Depends(get_db),
) -> Referral:
    referral = await _referral_repo.get(referral_id, db)
    if referral is None:
        raise NotFoundException("Referral")
    updated = await _referral_repo.update(referral_id, {"status": "hr_review"}, db)
    return updated


@router.post("/{referral_id}/reject", response_model=ReferralResponse)
async def reject_referral(
    referral_id: uuid.UUID,
    payload: RejectReferralRequest,
    current_user: Annotated[object, Depends(HR_ROLES)],
    db: AsyncSession = Depends(get_db),
) -> Referral:
    referral = await _referral_repo.get(referral_id, db)
    if referral is None:
        raise NotFoundException("Referral")
    updated = await _referral_repo.update(referral_id, {"status": "rejected"}, db)
    return updated


@router.post(
    "/{referral_id}/upload-resume",
    response_model=ResumeUploadResponse,
)
async def upload_resume(
    referral_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
) -> ResumeUploadResponse:
    if file.content_type != "application/pdf":
        raise BadRequestException("Only PDF files are allowed")
    if file.size and file.size > 10 * 1024 * 1024:
        raise BadRequestException("File size must not exceed 10 MB")

    referral = await _referral_repo.get(referral_id, db)
    if referral is None:
        raise NotFoundException("Referral")

    # Placeholder: In production, upload to Azure Blob and get URL
    resume_url = f"https://placeholder.blob.core.windows.net/resumes/{referral_id}/{file.filename}"
    await _referral_repo.update(referral_id, {"resume_url": resume_url}, db)

    return ResumeUploadResponse(
        referral_id=referral_id,
        resume_url=resume_url,
    )
