from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.workflow import (
    CompleteTaskRequest,
    ReassignTaskRequest,
    StartWorkflowResponse,
    WorkflowTaskResponse,
)
from app.api.auth.dependencies import CurrentUser, require_roles

router = APIRouter()
_wf_repo = WorkflowRepository()
HR_ROLES = require_roles(UserRole.HR, UserRole.PROGRAM_OWNER)


@router.post(
    "/start/{referral_id}",
    response_model=StartWorkflowResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_workflow(
    referral_id: uuid.UUID,
    current_user: Annotated[object, Depends(HR_ROLES)],
    db: AsyncSession = Depends(get_db),
) -> StartWorkflowResponse:
    tasks = await _wf_repo.create_workflow_tasks(referral_id, db)
    return StartWorkflowResponse(
        referral_id=referral_id,
        tasks_created=len(tasks),
        message="Workflow pipeline created successfully",
    )


@router.get("/referral/{referral_id}", response_model=list[WorkflowTaskResponse])
async def get_workflow_by_referral(
    referral_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> list[WorkflowTaskResponse]:
    tasks = await _wf_repo.get_by_referral(referral_id, db)
    return [WorkflowTaskResponse.model_validate(t) for t in tasks]


@router.get("/tasks", response_model=list[WorkflowTaskResponse])
async def list_my_tasks(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> list[WorkflowTaskResponse]:
    from sqlalchemy import select
    from app.models.workflow import WorkflowTask
    from app.core.constants import WorkflowTaskStatus

    result = await db.execute(
        select(WorkflowTask).where(
            WorkflowTask.assigned_to == current_user.id,
            WorkflowTask.status == WorkflowTaskStatus.IN_PROGRESS.value,
        )
    )
    tasks = result.scalars().all()
    return [WorkflowTaskResponse.model_validate(t) for t in tasks]


@router.post("/tasks/{task_id}/complete", response_model=WorkflowTaskResponse)
async def complete_task(
    task_id: uuid.UUID,
    payload: CompleteTaskRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> WorkflowTaskResponse:
    from datetime import datetime, timezone
    from app.core.constants import WorkflowTaskStatus, SLAStatus

    task = await _wf_repo.get(task_id, db)
    if task is None:
        raise NotFoundException("WorkflowTask")

    now = datetime.now(timezone.utc)
    sla = (
        SLAStatus.ON_TRACK.value
        if task.due_date and now <= task.due_date
        else SLAStatus.BREACHED.value
    )
    updated = await _wf_repo.update(
        task_id,
        {
            "status": WorkflowTaskStatus.COMPLETED.value,
            "completed_at": now,
            "sla_status": sla,
            "notes": payload.notes,
        },
        db,
    )
    return WorkflowTaskResponse.model_validate(updated)


@router.put("/tasks/{task_id}/reassign", response_model=WorkflowTaskResponse)
async def reassign_task(
    task_id: uuid.UUID,
    payload: ReassignTaskRequest,
    current_user: Annotated[object, Depends(HR_ROLES)],
    db: AsyncSession = Depends(get_db),
) -> WorkflowTaskResponse:
    task = await _wf_repo.get(task_id, db)
    if task is None:
        raise NotFoundException("WorkflowTask")
    updated = await _wf_repo.update(
        task_id,
        {"assigned_to": payload.assigned_to, "assigned_team": payload.assigned_team},
        db,
    )
    return WorkflowTaskResponse.model_validate(updated)
