from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Certificate, NDADocument
from app.repositories.base import BaseRepository


class NDARepository(BaseRepository[NDADocument]):
    def __init__(self) -> None:
        super().__init__(NDADocument)

    async def get_by_referral(
        self, referral_id: uuid.UUID, db: AsyncSession
    ) -> NDADocument | None:
        result = await db.execute(
            select(NDADocument).where(NDADocument.referral_id == referral_id)
        )
        return result.scalar_one_or_none()


class CertificateRepository(BaseRepository[Certificate]):
    def __init__(self) -> None:
        super().__init__(Certificate)

    async def get_by_referral(
        self, referral_id: uuid.UUID, db: AsyncSession
    ) -> Certificate | None:
        result = await db.execute(
            select(Certificate).where(Certificate.referral_id == referral_id)
        )
        return result.scalar_one_or_none()
