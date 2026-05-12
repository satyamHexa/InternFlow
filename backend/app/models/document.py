from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UUIDPrimaryKeyMixin


class NDADocument(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "nda_documents"

    referral_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("referrals.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    blob_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    signed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    signature_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ─────────────────────────────────────────────
    referral: Mapped["Referral"] = relationship(
        "Referral", back_populates="nda_document"
    )


class Certificate(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "certificates"

    referral_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("referrals.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    blob_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    generated_by: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────
    referral: Mapped["Referral"] = relationship(
        "Referral", back_populates="certificate"
    )
