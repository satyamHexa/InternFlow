from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

_SKIP_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}
_MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class AuditMiddleware(BaseHTTPMiddleware):
    """Lightweight request audit middleware.
    Logs mutating requests (POST/PUT/PATCH/DELETE) with timing info.
    Detailed per-resource audit entries are written by audit_service.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)

        if request.method in _MUTATING_METHODS:
            client_ip = (
                request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
                or (request.client.host if request.client else "unknown")
            )
            logger.info(
                "[AUDIT] %s %s %s | ip=%s | %sms",
                request.method,
                request.url.path,
                response.status_code,
                client_ip,
                elapsed_ms,
            )

        return response
