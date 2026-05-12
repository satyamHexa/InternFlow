from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.repositories.referral_repository import ReferralRepository
from app.repositories.document_repository import CertificateRepository
from app.schemas.document import (
    CertificateDownloadResponse,
    CertificateResponse,
    GenerateCertificateRequest,
)
from app.api.auth.dependencies import CurrentUser, require_roles

router = APIRouter()
_referral_repo = ReferralRepository()
_cert_repo = CertificateRepository()
HR_ROLES = require_roles(UserRole.HR, UserRole.PROGRAM_OWNER)


@router.post(
    "/generate",
    response_model=CertificateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_certificate(
    payload: GenerateCertificateRequest,
    current_user: Annotated[object, Depends(HR_ROLES)],
    db: AsyncSession = Depends(get_db),
) -> CertificateResponse:
    referral = await _referral_repo.get(payload.referral_id, db)
    if referral is None:
        raise NotFoundException("Referral")

    from app.services.certificate_service import certificate_service

    result = await certificate_service.generate_certificate(
        str(payload.referral_id),
        referral.candidate_name,
        str(current_user.id),
    )
    # Persist certificate record
    existing = await _cert_repo.get_by_referral(payload.referral_id, db)
    if existing:
        cert = await _cert_repo.update(
            existing.id, {"blob_url": result["blob_url"]}, db
        )
    else:
        cert = await _cert_repo.create(
            {
                "referral_id": payload.referral_id,
                "blob_url": result["blob_url"],
                "generated_by": current_user.id,
            },
            db,
        )
    return CertificateResponse.model_validate(cert)


@router.get("/{referral_id}", response_model=CertificateResponse)
async def get_certificate(
    referral_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> CertificateResponse:
    cert = await _cert_repo.get_by_referral(referral_id, db)
    if cert is None:
        raise NotFoundException("Certificate")
    return CertificateResponse.model_validate(cert)


@router.get("/{referral_id}/download-url", response_model=CertificateDownloadResponse)
async def get_download_url(
    referral_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> CertificateDownloadResponse:
    cert = await _cert_repo.get_by_referral(referral_id, db)
    if cert is None:
        raise NotFoundException("Certificate")

    from app.services.certificate_service import certificate_service

    url = await certificate_service.get_download_url(str(referral_id))
    return CertificateDownloadResponse(
        referral_id=referral_id,
        download_url=url,
        expires_in_seconds=3600,
    )
