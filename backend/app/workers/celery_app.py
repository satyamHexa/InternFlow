from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# ── Application factory ────────────────────────────────────────────
celery_app = Celery("internflow")

celery_app.conf.update(
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Periodic schedules
    beat_schedule={
        "evaluate-sla-hourly": {
            "task": "app.workers.sla_tasks.evaluate_sla_task",
            "schedule": crontab(minute=0),  # every hour
        },
        "escalate-sla-6h": {
            "task": "app.workers.sla_tasks.escalate_sla_task",
            "schedule": crontab(minute=0, hour="*/6"),
        },
    },
)

# Auto-discover tasks in workers package
celery_app.autodiscover_tasks(["app.workers"])
