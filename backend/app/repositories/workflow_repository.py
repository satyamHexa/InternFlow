from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import WorkflowTaskStatus, SLAStatus, SLA_TARGETS
from app.models.workflow import WorkflowTask
from app.repositories.base import BaseRepository


class WorkflowRepository(BaseRepository[WorkflowTask]):
    def __init__(self) -> None:
        super().__init__(WorkflowTask)

    async def get_by_referral(
        self, referral_id: uuid.UUID, db: AsyncSession
    ) -> Sequence[WorkflowTask]:
        result = await db.execute(
            select(WorkflowTask)
            .where(WorkflowTask.referral_id == referral_id)
            .order_by(WorkflowTask.stage_number)
        )
        return result.scalars().all()

    async def get_active_tasks(self, db: AsyncSession) -> Sequence[WorkflowTask]:
        result = await db.execute(
            select(WorkflowTask).where(
                WorkflowTask.status == WorkflowTaskStatus.IN_PROGRESS.value
            )
        )
        return result.scalars().all()

    async def get_breached_tasks(self, db: AsyncSession) -> Sequence[WorkflowTask]:
        result = await db.execute(
            select(WorkflowTask).where(
                WorkflowTask.sla_status == SLAStatus.BREACHED.value
            )
        )
        return result.scalars().all()

    async def create_workflow_tasks(
        self, referral_id: uuid.UUID, db: AsyncSession
    ) -> list[WorkflowTask]:
        """Create all 12 workflow tasks for a new referral."""
        from app.core.constants import SLA_TARGETS

        stage_names = [
            (1,  "Referral Submitted",      "HR"),
            (2,  "HR Review",                "HR"),
            (3,  "Eligibility Validation",   "HR"),
            (4,  "NDA Sent",                 "HR"),
            (5,  "NDA Signed",               "Candidate"),
            (6,  "Joining Form Completed",   "Candidate"),
            (7,  "Non-Worker ID Creation",   "IT"),
            (8,  "IT Provisioning",          "IT"),
            (9,  "Mentor Assignment",        "HR"),
            (10, "Internship Started",       "Program"),
            (11, "Internship Closed",        "Program"),
            (12, "Certificate Generated",   "HR"),
        ]

        now = datetime.now(timezone.utc)
        tasks: list[WorkflowTask] = []

        for stage_num, task_name, team in stage_names:
            sla_days = SLA_TARGETS.get(task_name, 3)
            from datetime import timedelta
            due_date = now + timedelta(days=sla_days)

            status = (
                WorkflowTaskStatus.IN_PROGRESS.value
                if stage_num == 1
                else WorkflowTaskStatus.PENDING.value
            )

            task = WorkflowTask(
                referral_id=referral_id,
                stage_number=stage_num,
                task_name=task_name,
                assigned_team=team,
                status=status,
                due_date=due_date,
                sla_status=SLAStatus.ON_TRACK.value,
            )
            db.add(task)
            tasks.append(task)

        await db.flush()
        for t in tasks:
            await db.refresh(t)

        return tasks
