from typing import Annotated, AsyncGenerator

import pydantic
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.utils.settings import CJMSBaseSettings


class _ConnectionURLs(CJMSBaseSettings):
    """URLs for connecting to other internal services."""

    DATABASE_URL: pydantic.SecretStr
    SENTRY_DSN: pydantic.SecretStr | None


ConnectionURLs = _ConnectionURLs()


class Connections:
    """How to connect to other, internal services."""

    DB_ENGINE = create_async_engine(ConnectionURLs.DATABASE_URL.get_secret_value())
    DB_SESSION_MAKER = async_sessionmaker(DB_ENGINE)


async def _get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """A dependency to pass a database session to every route function."""
    async with Connections.DB_SESSION_MAKER() as session:
        async with session.begin():
            yield session


DBSession = Annotated[AsyncSession, Depends(_get_db_session)]


class _Server(CJMSBaseSettings):
    """Basic configuration for the Code Jam Management System."""

    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False
    API_TOKEN: pydantic.SecretStr


Server = _Server(API_TOKEN="badbot13m0n8f570f942013fc818f234916ca531")
