"""Fixtures for tests of the `routers` package."""
import asyncpg
import pytest
from httpx import AsyncClient

from api import models


async def delete_jam(jam: models.CodeJamResponse, db: asyncpg.Connection) -> None:
    """Delete a jam and related contents from the database."""
    # Clean up the database. Ideally, this would have a `ON CASCADE`
    # delete on the database foreign keys, which would simplify deletion
    # here. An exercise for the reader!
    for team in jam.teams:
        await db.execute("DELETE FROM team_has_user WHERE team_id = $1", team.team_id)

    # As we do not have a filter we can apply here, the table is checked for
    # being empty at the caller site.
    await db.execute("DELETE FROM users")
    await db.execute("DELETE FROM teams WHERE jam_id = $1", jam.jam_id)
    await db.execute("DELETE FROM jams WHERE jam_id = $1", jam.jam_id)


@pytest.fixture(scope='session')
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
    client: AsyncClient, codejam: models.CodeJam, testdbconn: asyncpg.Connection
) -> models.CodeJam:
    """Create the codejam via the API and yield it."""
    # Ensure no users are in the database.
    current_users = await testdbconn.fetchval("SELECT count(*) FROM users")
    assert current_users == 0, "Users table is pre-populated"

    # Create the codejam and parse it into the expected
    # response model. This also double-checks proper response
    # structure.
    response = await client.post('/codejams', json=codejam.dict())
    assert response.status_code == 200, "Failed to create test codejam"
    created_jam = response.json()
    parsed = models.CodeJamResponse(**created_jam)

    try:
        yield parsed
    finally:
        await delete_jam(parsed, testdbconn)
