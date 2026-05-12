from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.core.database import get_db
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogResponse
from app.schemas.common import PaginatedResponse
from app.api.auth.dependencies import require_roles

router = APIRouter()
COMPLIANCE = require_roles(UserRole.COMPLIANCE_OFFICER, UserRole.HR)


@router.get("/logs", response_model=PaginatedResponse[AuditLogResponse])
async def list_audit_logs(
    current_user: Annotated[object, Depends(COMPLIANCE)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    action: str | None = None,
    module: str | None = None,
) -> PaginatedResponse[AuditLogResponse]:
    from sqlalchemy import func

    q = select(AuditLog)
    count_q = select(func.count(AuditLog.id))

    if action:
        q = q.where(AuditLog.action == action)
        count_q = count_q.where(AuditLog.action == action)
    if module:
        q = q.where(AuditLog.module == module)
        count_q = count_q.where(AuditLog.module == module)

    total = (await db.execute(count_q)).scalar_one()
    q = q.order_by(AuditLog.timestamp.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    items = result.scalars().all()

    return PaginatedResponse.create(
        items=[AuditLogResponse.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/logs/export/csv")
async def export_audit_csv(
    current_user: Annotated[object, Depends(COMPLIANCE)],
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    import csv
    import io

    result = await db.execute(
        select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(10000)
    )
    logs = result.scalars().all()

    def generate():
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["id", "user_id", "action", "module", "ip_address", "timestamp"])
        for log in logs:
            writer.writerow(
                [log.id, log.user_id, log.action, log.module, log.ip_address, log.timestamp]
            )
        yield buf.getvalue()

    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_logs.csv"},
    )
