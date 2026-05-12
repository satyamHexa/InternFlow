from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ReferralStatus, SLAStatus, UserRole
from app.core.database import get_db
from app.models.referral import Referral
from app.models.workflow import WorkflowTask
from app.schemas.dashboard import DashboardMetrics, DepartmentData, SLAReport
from app.api.auth.dependencies import require_roles

router = APIRouter()
HR_ONLY = require_roles(UserRole.HR, UserRole.PROGRAM_OWNER)


@router.get("/metrics", response_model=DashboardMetrics)
async def get_metrics(
    current_user: Annotated[object, Depends(HR_ONLY)],
    db: AsyncSession = Depends(get_db),
) -> DashboardMetrics:
    total = (await db.execute(select(func.count(Referral.id)))).scalar_one()
    pending_ndas = (
        await db.execute(
            select(func.count(Referral.id)).where(
                Referral.status == ReferralStatus.NDA_PENDING.value
            )
        )
    ).scalar_one()
    active = (
        await db.execute(
            select(func.count(Referral.id)).where(
                Referral.status == ReferralStatus.ACTIVE.value
            )
        )
    ).scalar_one()
    breaches = (
        await db.execute(
            select(func.count(WorkflowTask.id)).where(
                WorkflowTask.sla_status == SLAStatus.BREACHED.value
            )
        )
    ).scalar_one()

    return DashboardMetrics(
        total_referrals=total,
        pending_ndas=pending_ndas,
        active_interns=active,
        sla_breaches=breaches,
        delayed_onboarding=0,
        completed_this_month=0,
    )


@router.get("/referrals", response_model=list[DepartmentData])
async def get_referral_breakdown(
    current_user: Annotated[object, Depends(HR_ONLY)],
    db: AsyncSession = Depends(get_db),
) -> list[DepartmentData]:
    result = await db.execute(
        select(Referral.department, func.count(Referral.id))
        .group_by(Referral.department)
        .order_by(func.count(Referral.id).desc())
    )
    rows = result.all()
    return [DepartmentData(department=r[0], count=r[1]) for r in rows]


@router.get("/sla", response_model=list[SLAReport])
async def get_sla_report(
    current_user: Annotated[object, Depends(HR_ONLY)],
    db: AsyncSession = Depends(get_db),
) -> list[SLAReport]:
    result = await db.execute(
        select(
            WorkflowTask.task_name,
            WorkflowTask.sla_status,
            func.count(WorkflowTask.id),
        ).group_by(WorkflowTask.task_name, WorkflowTask.sla_status)
    )
    rows = result.all()

    aggregated: dict[str, dict] = {}
    for task_name, sla_status, count in rows:
        if task_name not in aggregated:
            aggregated[task_name] = {"on_track": 0, "at_risk": 0, "breached": 0}
        aggregated[task_name][sla_status.replace(" ", "_")] = count

    return [
        SLAReport(
            task_name=name,
            total=sum(d.values()),
            on_track=d.get("on_track", 0),
            at_risk=d.get("at_risk", 0),
            breached=d.get("breached", 0),
        )
        for name, d in aggregated.items()
    ]
