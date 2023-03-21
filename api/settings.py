import pydantic
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from api.utils.settings import CJMSBaseSettings


class _ConnectionURLs(CJMSBaseSettings):
    """URLs for connecting to other internal services."""

    DATABASE_URL: pydantic.SecretStr
    SENTRY_DSN: pydantic.SecretStr | None


ConnectionURLs = _ConnectionURLs()


class Connections:
    """How to connect to other, internal services."""

    DB_ENGINE = create_async_engine(ConnectionURLs.DATABASE_URL.get_secret_value())
    DB_SESSION = async_sessionmaker(DB_ENGINE)


class _Server(CJMSBaseSettings):
    """Basic configuration for the Code Jam Management System."""

    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False
    API_TOKEN: pydantic.SecretStr


Server = _Server(API_TOKEN="badbot13m0n8f570f942013fc818f234916ca531")
