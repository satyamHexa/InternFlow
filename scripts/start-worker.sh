#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
#  scripts/start-worker.sh
#  Start Celery worker and beat scheduler
# ──────────────────────────────────────────────────────────────
set -euo pipefail

cd "$(dirname "$0")/../backend"

echo "Starting Celery worker..."
celery -A app.workers.celery_app worker \
  --loglevel=info \
  --concurrency=4 \
  --queues=default,ai_tasks,notifications &

echo "Starting Celery beat scheduler..."
celery -A app.workers.celery_app beat \
  --loglevel=info

wait
