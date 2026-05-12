from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self) -> None:
        super().__init__(User)

    async def get_by_email(self, email: str, db: AsyncSession) -> User | None:
        result = await db.execute(
            select(User).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()

    async def get_by_role(self, role: str, db: AsyncSession) -> Sequence[User]:
        result = await db.execute(
            select(User).where(User.role == role, User.is_active.is_(True))
        )
        return result.scalars().all()

    async def deactivate(self, id: uuid.UUID, db: AsyncSession) -> User | None:
        return await self.update(id, {"is_active": False}, db)

    async def create(self, data: dict, db: AsyncSession) -> User:
        # Normalise email before storing
        if "email" in data:
            data["email"] = data["email"].lower().strip()
        return await super().create(data, db)
