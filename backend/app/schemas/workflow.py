from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import WorkflowTaskStatus, SLAStatus


class WorkflowTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    referral_id: uuid.UUID
    stage_number: int
    task_name: str
    assigned_to: uuid.UUID | None
    assigned_team: str | None
    status: str
    due_date: datetime | None
    completed_at: datetime | None
    sla_status: str
    notes: str | None
    created_at: datetime


class CompleteTaskRequest(BaseModel):
    notes: str | None = Field(default=None, max_length=2000)


class ReassignTaskRequest(BaseModel):
    assigned_to: uuid.UUID
    assigned_team: str | None = None


class SLAReportItem(BaseModel):
    task_name: str
    total: int
    on_track: int
    at_risk: int
    breached: int


class StartWorkflowResponse(BaseModel):
    referral_id: uuid.UUID
    tasks_created: int
    message: str
