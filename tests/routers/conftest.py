"""Fixtures for tests of the `routers` package."""
import pytest
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import FastAPI

from api import models
from api.database import Jam, Team, TeamUser, User


async def delete_jam(jam: models.CodeJamResponse, session: AsyncSession) -> None:
    """Delete a jam and related contents from the database."""
    # Clean up the database. Ideally, this would have a `ON CASCADE`
    # delete on the database foreign keys, which would simplify deletion
    # here. An exercise for the reader!
    for team in jam.teams:
        await session.execute(delete(TeamUser).where(TeamUser.team_id == team.id))

    # As we do not have a filter we can apply here, the table is checked for
    # being empty at the caller site.
    await session.execute(delete(User))
    await session.execute(delete(Team).where(Team.jam_id == jam.id))
    await session.execute(delete(Jam).where(Jam.id == jam.id))


@pytest.fixture
def codejam() -> models.CodeJam:
    """Build a codejam for test purposes."""
    return models.CodeJam(
        name='Python Discord Test Jam 1 - Break your coverage!',
        teams=[
            models.Team(
                name='lemoncluster 1',
                users=[
                    models.User(user_id=1337, is_leader=True),
                    models.User(user_id=109248, is_leader=False),
                ]
            ),
        ]
    )


@pytest.fixture
async def created_codejam(
    client: AsyncClient, codejam: models.CodeJam, session: AsyncSession
) -> models.CodeJam:
    """Create the codejam via the API and yield it."""
    # Ensure no users are in the database.
    current_users = len((await session.execute(select(User))).unique().scalars().all())
    assert current_users == 0, "Users table is pre-populated"

    # Create the codejam and parse it into the expected
    # response model. This also double-checks proper response
    # structure.
    response = await client.post('/codejams', json=codejam.dict())
    assert response.status_code == 200, "Failed to create test codejam"
    created_jam = response.json()
    parsed = models.CodeJamResponse(**created_jam)
    yield parsed
    await delete_jam(parsed, session)
