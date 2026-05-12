from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.constants import ReferralStatus
from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Referral(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "referrals"

    candidate_name: Mapped[str] = mapped_column(String(255), nullable=False)
    candidate_email: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    candidate_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    referrer_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    mentor_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    department: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=ReferralStatus.DRAFT.value,
        index=True,
    )
    resume_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_resume_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_duplicate: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    duplicate_of_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("referrals.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────
    referrer: Mapped["User"] = relationship(
        "User", foreign_keys=[referrer_id], back_populates="referrals_made"
    )
    mentor: Mapped["User | None"] = relationship(
        "User", foreign_keys=[mentor_id], back_populates="referrals_mentored"
    )
    workflow_tasks: Mapped[list["WorkflowTask"]] = relationship(
        "WorkflowTask",
        back_populates="referral",
        cascade="all, delete-orphan",
        order_by="WorkflowTask.stage_number",
    )
    nda_document: Mapped["NDADocument | None"] = relationship(
        "NDADocument", back_populates="referral", uselist=False
    )
    certificate: Mapped["Certificate | None"] = relationship(
        "Certificate", back_populates="referral", uselist=False
    )
    onboarding_tasks: Mapped[list["OnboardingTask"]] = relationship(
        "OnboardingTask",
        back_populates="referral",
        cascade="all, delete-orphan",
        lazy="select",
    )
