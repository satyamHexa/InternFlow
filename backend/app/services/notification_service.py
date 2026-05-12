from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification

logger = logging.getLogger(__name__)


class NotificationService:
    """Fan-out notification service.
    In-app notifications are persisted immediately.
    Email/Teams are dispatched via Celery workers.
    """

    async def send(
        self,
        *,
        user_id: uuid.UUID,
        event: str,
        title: str,
        message: str,
        db: AsyncSession,
        channel: str = "in_app",
        referral_id: uuid.UUID | None = None,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            event=event,
            title=title,
            message=message,
            channel=channel,
            is_read=False,
            referral_id=referral_id,
        )
        db.add(notification)
        await db.flush()
        await db.refresh(notification)

        # Dispatch async tasks for email/Teams
        if channel in ("email", "all"):
            self._dispatch_email(user_id, title, message)
        if channel in ("teams", "all"):
            self._dispatch_teams(title, message)

        return notification

    def _dispatch_email(self, user_id: uuid.UUID, subject: str, body: str) -> None:
        """Enqueue Celery email task."""
        try:
            from app.workers.notification_tasks import send_email_task
            send_email_task.delay(str(user_id), subject, body)
        except Exception as exc:
            logger.warning("Failed to dispatch email task: %s", exc)

    def _dispatch_teams(self, title: str, message: str) -> None:
        """Enqueue Celery Teams task."""
        try:
            from app.workers.notification_tasks import send_teams_task
            send_teams_task.delay(title, message)
        except Exception as exc:
            logger.warning("Failed to dispatch Teams task: %s", exc)


notification_service = NotificationService()
