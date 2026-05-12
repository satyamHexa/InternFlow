from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.referral import Referral
from app.repositories.base import BaseRepository


class ReferralRepository(BaseRepository[Referral]):
    def __init__(self) -> None:
        super().__init__(Referral)

    async def find_duplicate(
        self,
        candidate_email: str,
        db: AsyncSession,
        exclude_id: uuid.UUID | None = None,
    ) -> Referral | None:
        """Exact-match duplicate check by candidate email."""
        q = select(Referral).where(
            Referral.candidate_email == candidate_email.lower().strip()
        )
        if exclude_id:
            q = q.where(Referral.id != exclude_id)
        result = await db.execute(q)
        return result.scalars().first()

    async def get_by_referrer(
        self, referrer_id: uuid.UUID, db: AsyncSession
    ) -> Sequence[Referral]:
        result = await db.execute(
            select(Referral)
            .where(Referral.referrer_id == referrer_id)
            .order_by(Referral.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_status(
        self, status: str, db: AsyncSession
    ) -> Sequence[Referral]:
        result = await db.execute(
            select(Referral)
            .where(Referral.status == status)
            .order_by(Referral.created_at.desc())
        )
        return result.scalars().all()

    async def create(self, data: dict, db: AsyncSession) -> Referral:
        if "candidate_email" in data:
            data["candidate_email"] = data["candidate_email"].lower().strip()
        return await super().create(data, db)
