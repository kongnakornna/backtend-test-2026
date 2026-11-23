from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.pool import StaticPool

import src.infrastructure.models  # noqa: F401
from src.infrastructure.db.base import Base
from src.infrastructure.db.session import build_engine
from src.main import create_app
from src.presentation.dependencies.database import get_session


@pytest.fixture
async def session_factory() -> AsyncIterator[async_sessionmaker]:
    # Fresh in-memory database per test; StaticPool keeps one shared connection.
    engine = build_engine(
        "sqlite+aiosqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


@pytest.fixture
async def client(session_factory: async_sessionmaker) -> AsyncIterator[AsyncClient]:
    app = create_app()

    async def override_get_session():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as http:
        yield http
