from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self) -> None:
        super().__init__(Notification)

    async def get_for_user(
        self,
        user_id: uuid.UUID,
        db: AsyncSession,
        *,
        unread_only: bool = False,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[Notification], int]:
        from sqlalchemy import func

        filters = [Notification.user_id == user_id]
        if unread_only:
            filters.append(Notification.is_read == False)  # noqa: E712
        return await self.list(db, filters=filters, offset=offset, limit=limit)

    async def mark_read(self, notification_id: uuid.UUID, db: AsyncSession) -> Notification | None:
        return await self.update(notification_id, {"is_read": True}, db)

    async def mark_all_read(self, user_id: uuid.UUID, db: AsyncSession) -> int:
        from sqlalchemy import update

        result = await db.execute(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
            .values(is_read=True)
        )
        return result.rowcount

    async def unread_count(self, user_id: uuid.UUID, db: AsyncSession) -> int:
        from sqlalchemy import func

        result = await db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.is_read == False,  # noqa: E712
            )
        )
        return result.scalar_one()
