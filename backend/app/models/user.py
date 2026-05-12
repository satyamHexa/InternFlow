from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ── Relationships ─────────────────────────────────────────────
    referrals_made: Mapped[list["Referral"]] = relationship(
        "Referral",
        foreign_keys="Referral.referrer_id",
        back_populates="referrer",
        lazy="select",
    )
    referrals_mentored: Mapped[list["Referral"]] = relationship(
        "Referral",
        foreign_keys="Referral.mentor_id",
        back_populates="mentor",
        lazy="select",
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog", back_populates="user", lazy="select"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="user", lazy="select"
    )
    workflow_tasks: Mapped[list["WorkflowTask"]] = relationship(
        "WorkflowTask",
        foreign_keys="WorkflowTask.assigned_to",
        back_populates="assignee",
        lazy="select",
    )
    onboarding_tasks: Mapped[list["OnboardingTask"]] = relationship(
        "OnboardingTask",
        foreign_keys="OnboardingTask.assigned_to",
        back_populates="assignee",
        lazy="select",
    )
