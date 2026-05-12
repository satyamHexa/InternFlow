from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.main import app

# ── Test database (SQLite in-memory) ─────────────────────────────────
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestSession = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSession() as session:
        try:
            yield session
            await session.rollback()  # Roll back after each test
        finally:
            await session.close()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


# ── Auth helper fixtures ──────────────────────────────────────────
import uuid
from app.models.user import User


@pytest_asyncio.fixture
async def hr_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid.uuid4(),
        name="HR Admin",
        email="hr@internflow.test",
        role="hr",
        password_hash=hash_password("TestPass123!"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def employee_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid.uuid4(),
        name="Employee One",
        email="employee@internflow.test",
        role="employee",
        password_hash=hash_password("TestPass123!"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest.fixture
def hr_auth_headers(hr_user: User) -> dict[str, str]:
    token = create_access_token({"sub": str(hr_user.id), "role": hr_user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def employee_auth_headers(employee_user: User) -> dict[str, str]:
    token = create_access_token({"sub": str(employee_user.id), "role": employee_user.role})
    return {"Authorization": f"Bearer {token}"}
