from __future__ import annotations

# Rate limiting is handled via slowapi (wraps limits library).
# The Limiter instance is created here and registered in main.py.
#
# Per-endpoint override example:
#   @router.post("/ai/parse-resume")
#   @limiter.limit("5/minute")
#   async def parse_resume(request: Request): ...

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# Use Redis for distributed rate limiting in production; fall back to
# in-process memory for local development (single-worker only).
_storage_uri = settings.REDIS_URL if settings.REDIS_URL else "memory://"

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
    storage_uri=_storage_uri,
)
