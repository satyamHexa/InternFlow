from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.onboarding import OnboardingTask
from app.repositories.base import BaseRepository


class OnboardingRepository(BaseRepository[OnboardingTask]):
    def __init__(self) -> None:
        super().__init__(OnboardingTask)

    async def get_by_referral(
        self,
        referral_id: uuid.UUID,
        db: AsyncSession,
        *,
        status_filter: str | None = None,
        category_filter: str | None = None,
    ) -> Sequence[OnboardingTask]:
        filters = [OnboardingTask.referral_id == referral_id]
        if status_filter:
            filters.append(OnboardingTask.status == status_filter)
        if category_filter:
            filters.append(OnboardingTask.category == category_filter)

        items, _ = await self.list(db, filters=filters, limit=200)
        return items

    async def get_assigned_to(
        self, user_id: uuid.UUID, db: AsyncSession
    ) -> Sequence[OnboardingTask]:
        items, _ = await self.list(
            db,
            filters=[OnboardingTask.assigned_to == user_id],
            limit=200,
        )
        return items

    async def bulk_create(
        self, tasks: list[dict], db: AsyncSession
    ) -> list[OnboardingTask]:
        created = []
        for data in tasks:
            obj = await self.create(data, db)
            created.append(obj)
        return created
