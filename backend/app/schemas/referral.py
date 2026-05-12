from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.constants import ReferralStatus


class CreateReferralRequest(BaseModel):
    candidate_name: str = Field(min_length=2, max_length=255)
    candidate_email: EmailStr
    candidate_phone: str | None = Field(default=None, max_length=50)
    department: str = Field(min_length=2, max_length=255)
    mentor_id: uuid.UUID | None = None


class UpdateReferralRequest(BaseModel):
    candidate_name: str | None = Field(default=None, min_length=2, max_length=255)
    candidate_phone: str | None = None
    department: str | None = None
    mentor_id: uuid.UUID | None = None
    status: ReferralStatus | None = None


class ReferralResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    candidate_name: str
    candidate_email: str
    candidate_phone: str | None
    referrer_id: uuid.UUID
    mentor_id: uuid.UUID | None
    department: str
    status: str
    resume_url: str | None
    confidence_score: float | None
    is_duplicate: bool
    created_at: datetime
    updated_at: datetime


class ReferralDetailResponse(ReferralResponse):
    parsed_resume_json: dict[str, Any] | None = None


class RejectReferralRequest(BaseModel):
    reason: str = Field(min_length=10)


class ResumeUploadResponse(BaseModel):
    referral_id: uuid.UUID
    resume_url: str
    message: str = "Resume uploaded successfully"
