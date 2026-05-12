from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """Write-only audit trail service. Never raises — audit failures are
    logged to the structured log but never interrupt the main request."""

    async def log(
        self,
        *,
        user_id: uuid.UUID | None,
        action: str,
        module: str,
        db: AsyncSession,
        metadata: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> None:
        try:
            entry = AuditLog(
                user_id=user_id,
                action=action,
                module=module,
                metadata_json=metadata or {},
                ip_address=ip_address,
            )
            db.add(entry)
            await db.flush()
        except Exception as exc:
            logger.warning("Audit log failed (non-fatal): %s", exc)


audit_service = AuditService()
