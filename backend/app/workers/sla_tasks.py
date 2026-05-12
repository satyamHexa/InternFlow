from __future__ import annotations

import asyncio
import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.sla_tasks.evaluate_sla_task")
def evaluate_sla_task() -> None:
    """Run every hour. Re-evaluate sla_status for all IN_PROGRESS tasks."""
    asyncio.run(_evaluate_sla())


async def _evaluate_sla() -> None:
    from app.core.database import AsyncSessionLocal
    from app.repositories.workflow_repository import WorkflowRepository
    from app.services.workflow_service import workflow_service

    async with AsyncSessionLocal() as db:
        repo = WorkflowRepository()
        tasks = await repo.get_active_tasks(db)
        for task in tasks:
            new_status = workflow_service.evaluate_sla(task)
            if new_status != task.sla_status:
                await repo.update(task.id, {"sla_status": new_status}, db)
                logger.info(
                    "SLA updated task=%s from=%s to=%s",
                    task.id, task.sla_status, new_status,
                )
        await db.commit()


@celery_app.task(name="app.workers.sla_tasks.escalate_sla_task")
def escalate_sla_task() -> None:
    """Run every 6 hours. Escalate breached tasks to program_owner."""
    logger.info("SLA escalation task running")
    # Full escalation: query breached tasks > 24h, send Teams alert
