"""Fixtures for tests of the `routers` package."""
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api import models
from api.database import Infraction, Jam, Team, TeamUser, User, Winner


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
        ongoing=True,
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


@pytest.fixture
async def created_infraction(
    client: AsyncClient,
    app: FastAPI,
    session: AsyncSession,
    created_codejam: models.CodeJamResponse
) -> models.InfractionResponse:
    """Create a test Infraction via the API and yield it."""
    # Select one of the test users, so that we can issue an infraction to that user
    user_id = created_codejam.teams[0].users[0].user_id
    jam_id = created_codejam.id
    response = await client.post(
        app.url_path_for("create_infraction"),
        json={"user_id": user_id, "jam_id": jam_id, "reason": "Too good to be true", "infraction_type": "warning"}
    )
    parsed_infraction = models.InfractionResponse(**response.json())
    assert response.status_code == 200
    # Check whether the infraction was actually created, and insterted into the db
    assert (
        await (session.execute(select(Infraction).where(Infraction.id == parsed_infraction.id)))
    ).unique().scalars().one_or_none(), "Failed to create Infraction"
    yield parsed_infraction


@pytest.fixture
async def created_winner(
    client: AsyncClient,
    app: FastAPI,
    session: AsyncSession,
    created_codejam: models.CodeJamResponse
) -> models.WinnerResponse:
    """Create a single test Winner via the API and yield it."""
    # Select a test user, so that we can use it to create the winner
    user_id = created_codejam.teams[0].users[0].user_id
    jam_id = created_codejam.id
    response = await client.post(
        app.url_path_for("create_winners", jam_id=jam_id),
        json=[{"user_id": user_id, "first_place": True}]
    )

    assert response.status_code == 200
    [raw_winner] = response.json()  # There should be exactly one winner
    parsed_winner = models.WinnerResponse(**raw_winner)

    assert (
        await session.execute(select(Winner).where(Winner.user_id == parsed_winner.user_id))
    ).unique().scalars().one_or_none(), "Failed to create Winner"

    yield parsed_winner
