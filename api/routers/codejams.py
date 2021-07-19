from typing import Any

import asyncpg
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.database import Jam, Team, User, TeamUser
from api.dependencies import get_db_session
from api.models import CodeJam, CodeJamResponse


router = APIRouter(prefix="/codejams", tags=["codejams"])


async def get_codejam_data(conn: asyncpg.Connection, jam_id: int, jam_name: str) -> dict[str, Any]:
    """Gets all the data stored in the database about the specified codejam."""
    codejam = {"jam_id": jam_id, "name": jam_name}

    db_teams = await conn.fetch(
        "SELECT team_id, team_name FROM teams WHERE jam_id = $1", jam_id
    )

    teams = []

    for team_id, team_name in db_teams:

        team = {}
        users = []

        db_users = await conn.fetch(
            "SELECT user_id, is_leader from team_has_user WHERE team_id = $1",
            team_id,
        )

        for user_id, is_leader in db_users:
            users.append(dict(user_id=user_id, is_leader=is_leader))

        team["users"] = users
        team["name"] = team_name
        team["team_id"] = team_id
        teams.append(team)

    codejam["teams"] = teams

    codejam["infractions"] = [
        dict(infraction)
        for infraction in await conn.fetch(
            "SELECT * FROM infractions WHERE jam_id = $1", jam_id
        )
    ]

    codejam["winners"] = [
        dict(winner)
        for winner in await conn.fetch(
            "SELECT user_id, first_place FROM winners WHERE jam_id = $1", jam_id
        )
    ]

    return codejam


@router.get("/", response_model=list[CodeJamResponse])
async def get_codejams(session: AsyncSession = Depends(get_db_session)) -> list[dict[str, Any]]:
    """Get all the codejams stored in the database."""
    codejams = await session.execute(select(Jam).order_by(desc(Jam.id)))
    codejams.unique()

    return codejams.scalars().all()


@router.get(
    "/{codejam_id}",
    response_model=CodeJamResponse,
    responses={
        404: {
            "description": "CodeJam could not be found."
        }
    }
)
async def get_codejam(codejam_id: int, session: AsyncSession = Depends(get_db_session)) -> dict[str, Any]:
    """Get a specific codejam stored in the database by ID."""
    jam_result = await session.execute(select(Jam).where(Jam.id == codejam_id))
    jam_result.unique()

    if not (jam := jam_result.scalars().one_or_none()):
        raise HTTPException(status_code=404, detail="CodeJam with specified ID could not be found.")

    return jam


@router.post("/", response_model=CodeJamResponse)
async def create_codejam(codejam: CodeJam, session: AsyncSession = Depends(get_db_session)) -> dict[str, Any]:
    """Create a new codejam and get back the one just created."""
    jam = Jam(name=codejam.name)
    session.add(jam)
    # Flush here to receive jam ID
    await session.flush()

    for raw_team in codejam.teams:
        team = Team(jam_id=jam.id, name=raw_team.name)
        session.add(team)
        # Flush here to receive team ID
        await session.flush()

        for raw_user in raw_team.users:
            if not (
                    await session.execute(select(User).where(User.id == raw_user.user_id))
            ).unique().scalars().one_or_none():
                user = User(id=raw_user.user_id)
                session.add(user)

            team_user = TeamUser(team_id=team.id, user_id=raw_user.user_id, is_leader=raw_user.is_leader)
            session.add(team_user)

    await session.flush()

    # Pydantic, what is synchronous, may attempt to call async methods if current jam
    # object is returned. To avoid this, fetch all data here, in async context.
    jam_result = await session.execute(select(Jam).where(Jam.id == jam.id))
    jam_result.unique()

    jam = jam_result.scalars().one()

    return jam
