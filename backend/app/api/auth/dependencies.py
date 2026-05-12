from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import verify_token
from app.core.constants import UserRole
from app.models.user import User
from app.repositories.user_repository import UserRepository

_bearer_scheme = HTTPBearer(auto_error=False)
_user_repo = UserRepository()


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)
    ],
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise UnauthorizedException("No Bearer token provided")

    payload = verify_token(credentials.credentials, expected_type="access")
    sub = payload.get("sub")
    if sub is None:
        raise UnauthorizedException()

    user = await _user_repo.get(uuid.UUID(sub), db)
    if user is None or not user.is_active:
        raise UnauthorizedException("User not found or inactive")

    return user


def require_roles(*roles: UserRole):
    """Return a FastAPI dependency that enforces role membership."""

    async def _check(
        current_user: User = Depends(get_current_user),
    ) -> User:
        allowed = {r.value for r in roles}
        if current_user.role not in allowed:
            raise ForbiddenException(
                f"Requires role: {', '.join(allowed)}"
            )
        return current_user

    return _check


# Convenience alias used in route signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
