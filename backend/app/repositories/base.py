from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Generic, Sequence, TypeVar

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)

# Sentinel: attribute name present on soft-deletable models
_SOFT_DELETE_COL = "deleted_at"


def _is_soft_deletable(model: type) -> bool:
    return hasattr(model, _SOFT_DELETE_COL)


class BaseRepository(Generic[ModelType]):
    """Generic async repository using the Repository pattern.

    Automatically applies soft-delete filtering for models that carry a
    ``deleted_at`` column (via ``SoftDeleteMixin``).
    Business logic must NOT live here — data access only.
    """

    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    # ── helpers ────────────────────────────────────────────────────────────
    def _active_filter(self) -> list[Any]:
        if _is_soft_deletable(self.model):
            return [getattr(self.model, _SOFT_DELETE_COL).is_(None)]
        return []

    # ── read ───────────────────────────────────────────────────────────────
    async def get(
        self, id: uuid.UUID, db: AsyncSession, *, include_deleted: bool = False
    ) -> ModelType | None:
        q = select(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        if not include_deleted:
            for f in self._active_filter():
                q = q.where(f)
        result = await db.execute(q)
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        filters: list[Any] | None = None,
        offset: int = 0,
        limit: int = 20,
        order_by: Any | None = None,
        include_deleted: bool = False,
    ) -> tuple[Sequence[ModelType], int]:
        q = select(self.model)
        count_q = select(func.count()).select_from(self.model)

        all_filters = ([] if include_deleted else self._active_filter()) + (filters or [])
        for f in all_filters:
            q = q.where(f)
            count_q = count_q.where(f)

        if order_by is not None:
            q = q.order_by(order_by)

        total_result = await db.execute(count_q)
        total = total_result.scalar_one()

        q = q.offset(offset).limit(limit)
        result = await db.execute(q)
        return result.scalars().all(), total

    # ── write ──────────────────────────────────────────────────────────────
    async def create(
        self, data: dict[str, Any], db: AsyncSession
    ) -> ModelType:
        obj = self.model(**data)
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def update(
        self,
        id: uuid.UUID,
        data: dict[str, Any],
        db: AsyncSession,
    ) -> ModelType | None:
        obj = await self.get(id, db)
        if obj is None:
            return None
        for key, value in data.items():
            setattr(obj, key, value)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def delete(
        self, id: uuid.UUID, db: AsyncSession, *, hard: bool = False
    ) -> bool:
        """Soft-delete when the model supports it (default); hard-delete otherwise or when hard=True."""
        obj = await self.get(id, db)
        if obj is None:
            return False
        if not hard and _is_soft_deletable(self.model):
            setattr(obj, _SOFT_DELETE_COL, datetime.now(timezone.utc))
            await db.flush()
        else:
            await db.delete(obj)
        return True

    async def restore(self, id: uuid.UUID, db: AsyncSession) -> ModelType | None:
        """Undelete a soft-deleted record."""
        obj = await self.get(id, db, include_deleted=True)
        if obj is None or not _is_soft_deletable(self.model):
            return None
        setattr(obj, _SOFT_DELETE_COL, None)
        await db.flush()
        await db.refresh(obj)
        return obj
