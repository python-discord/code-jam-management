from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

import api.database as db


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """A dependency to pass a database session to every route function."""
    async with db.Session() as session:
        async with session.begin():
            yield session
