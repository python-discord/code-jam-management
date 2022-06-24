"""Shared fixtures for pytest."""

import asyncio
from typing import Callable, Generator
from urllib.parse import urlsplit, urlunsplit

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from api.constants import Config
from api.database import Base
from api.dependencies import get_db_session
from api.main import app as main_app

test_engine = create_async_engine(Config.DATABASE_URL, future=True, isolation_level="AUTOCOMMIT")


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Yields back an asyncio event loop, then closes it."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def create_test_database_engine() -> Generator:
    """Yield back a Database engine object."""
    async with test_engine.begin() as conn:
        await conn.execute(text("CREATE DATABASE test;"))
        test_db_url = urlsplit(Config.DATABASE_URL)._replace(path="/test")
        engine = create_async_engine(urlunsplit(test_db_url), future=True)
        yield engine
        await engine.dispose()
        await conn.execute(text("DROP DATABASE test;"))


@pytest.fixture()
async def session(create_test_database_engine: AsyncEngine) -> AsyncSession:
    """Yields back an Asynchronous database session."""
    async with create_test_database_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        async with AsyncSession(bind=conn, expire_on_commit=False) as session:
            yield session
            await session.close()


@pytest.fixture()
def override_db_session(session: AsyncSession) -> AsyncSession:
    """Yields back the modified Database session that uses the correspondent Database."""

    async def _override_db_session() -> AsyncSession:
        yield session

    yield _override_db_session


@pytest.fixture()
def app(override_db_session: Callable) -> FastAPI:
    """Overrides the default FastAPI app to use the overridden DB session."""
    main_app.dependency_overrides[get_db_session] = override_db_session
    yield main_app


@pytest.fixture()
async def client(app: FastAPI) -> AsyncClient:
    """Return a client for testing the app."""
    async with AsyncClient(app=app, base_url='http://testserver') as ac:
        yield ac
