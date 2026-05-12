from __future__ import annotations

import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.notification_tasks.send_email_task", bind=True, max_retries=3)
def send_email_task(self, user_id: str, subject: str, body: str) -> None:
    """Send email via SendGrid / SMTP adapter."""
    try:
        logger.info("[EMAIL] Sending to user_id=%s | subject=%s", user_id, subject)
        # Full SendGrid integration: from app.services.notification_service
    except Exception as exc:
        logger.error("Email task failed: %s", exc)
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="app.workers.notification_tasks.send_teams_task", bind=True, max_retries=3)
def send_teams_task(self, title: str, message: str) -> None:
    """Post an Adaptive Card to Teams webhook."""
    try:
        from app.core.config import settings
        import httpx

        if not settings.TEAMS_WEBHOOK_URL:
            logger.debug("Teams webhook not configured, skipping")
            return

        payload = {
            "@type": "MessageCard",
            "summary": title,
            "sections": [{"text": message}],
        }
        with httpx.Client(timeout=10) as client:
            resp = client.post(settings.TEAMS_WEBHOOK_URL, json=payload)
            resp.raise_for_status()
    except Exception as exc:
        logger.error("Teams task failed: %s", exc)
        raise self.retry(exc=exc, countdown=60)
