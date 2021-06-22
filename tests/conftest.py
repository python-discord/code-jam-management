"""Shared fixtures for pytest."""

import asyncio
import contextlib
from pathlib import Path

import asyncpg
import pytest
from httpx import AsyncClient

from api.constants import DATABASE_POOL
from api.main import app


@pytest.fixture(scope='session')
def event_loop() -> asyncio.AbstractEventLoop:
    """Create the event loop to use for testing."""
    # This is normally defined by `pytest-asyncio`, but
    # in order to use session-scoped fixtures, we need to
    # override it manually.

    return asyncio.get_event_loop()


@pytest.fixture(scope='session')
async def testdbpool() -> asyncpg.Pool:
    """Set up and return the test database pool."""
    return await DATABASE_POOL


@pytest.fixture(scope='session')
async def testdbconn(testdbpool: asyncpg.Pool) -> asyncpg.Connection:
    """Yield a connection from the test database."""
    async with testdbpool.acquire() as conn:
        yield conn


@pytest.fixture(autouse=True, scope='session')
async def initialize_database(testdbconn: asyncpg.Connection) -> None:
    """Set up the database from SQL in `postgres/` directory."""
    rootdir = Path(__file__).parent.parent.absolute()
    sqldir = rootdir / 'postgres'
    for path in sqldir.iterdir():
        await testdbconn.execute(path.read_text())


@pytest.fixture
async def client() -> contextlib.AbstractContextManager[AsyncClient]:
    """Return a client for testing the app."""
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac
