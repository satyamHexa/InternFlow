from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import SLAStatus, WorkflowTaskStatus
from app.models.workflow import WorkflowTask
from app.repositories.workflow_repository import WorkflowRepository

_wf_repo = WorkflowRepository()


class WorkflowService:
    async def create_pipeline(
        self, referral_id: uuid.UUID, db: AsyncSession
    ) -> list[WorkflowTask]:
        """Initialise the 12-stage workflow for a referral."""
        return await _wf_repo.create_workflow_tasks(referral_id, db)

    async def complete_task(
        self,
        task_id: uuid.UUID,
        notes: str | None,
        db: AsyncSession,
    ) -> WorkflowTask:
        """Mark a task complete and evaluate SLA."""
        task = await _wf_repo.get(task_id, db)
        if task is None:
            raise ValueError(f"Task {task_id} not found")

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
                "notes": notes,
            },
            db,
        )

        # Advance the next pending stage to IN_PROGRESS
        tasks = await _wf_repo.get_by_referral(task.referral_id, db)
        for t in tasks:
            if t.stage_number == task.stage_number + 1:
                await _wf_repo.update(
                    t.id,
                    {"status": WorkflowTaskStatus.IN_PROGRESS.value},
                    db,
                )
                break

        return updated

    def evaluate_sla(self, task: WorkflowTask) -> str:
        if task.due_date is None:
            return SLAStatus.ON_TRACK.value
        now = datetime.now(timezone.utc)
        # Normalise naive datetimes coming from the DB to UTC
        if task.due_date.tzinfo is None:
            due = task.due_date.replace(tzinfo=timezone.utc)
        else:
            due = task.due_date
        remaining = (due - now).total_seconds()
        if remaining < 0:
            return SLAStatus.BREACHED.value
        if remaining < 86400:  # < 24h
            return SLAStatus.AT_RISK.value
        return SLAStatus.ON_TRACK.value


workflow_service = WorkflowService()
