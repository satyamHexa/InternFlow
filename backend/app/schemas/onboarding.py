from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateOnboardingTaskRequest(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    description: str | None = None
    category: str = Field(min_length=2, max_length=100)
    assigned_to: uuid.UUID | None = None
    due_date: datetime | None = None


class UpdateOnboardingTaskRequest(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    category: str | None = None
    assigned_to: uuid.UUID | None = None
    due_date: datetime | None = None
    status: str | None = None
    notes: str | None = None


class CompleteOnboardingTaskRequest(BaseModel):
    notes: str | None = None


class OnboardingTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    referral_id: uuid.UUID
    assigned_to: uuid.UUID | None
    title: str
    description: str | None
    category: str
    status: str
    due_date: datetime | None
    completed_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
