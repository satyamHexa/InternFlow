from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NDADocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    referral_id: uuid.UUID
    blob_url: str | None
    signed_at: datetime | None
    generated_at: datetime


class CertificateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    referral_id: uuid.UUID
    blob_url: str | None
    generated_at: datetime
    generated_by: uuid.UUID | None


class GenerateCertificateRequest(BaseModel):
    referral_id: uuid.UUID


class CertificateDownloadResponse(BaseModel):
    referral_id: uuid.UUID
    download_url: str
    expires_in_seconds: int = 3600
