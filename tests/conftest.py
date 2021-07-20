"""Shared fixtures for pytest."""

import asyncio
import contextlib

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import Session
from api.main import app


@pytest.fixture(scope='session')
def event_loop() -> asyncio.AbstractEventLoop:
    """Create the event loop to use for testing."""
    # This is normally defined by `pytest-asyncio`, but
    # in order to use session-scoped fixtures, we need to
    # override it manually.

    return asyncio.get_event_loop()


@pytest.fixture(scope='session')
async def session() -> AsyncSession:
    """Yield a SQLAlchemy async session."""
    async with Session() as async_session:
        async with async_session.begin():
            return async_session


@pytest.fixture
async def client() -> contextlib.AbstractContextManager[AsyncClient]:
    """Return a client for testing the app."""
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac
