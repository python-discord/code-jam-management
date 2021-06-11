from typing import Any

import asyncpg
from fastapi import APIRouter, HTTPException, Request

from api.models import CodeJam, CodeJamResponse


router = APIRouter(prefix="/codejams", tags=["codejams"])


async def fetch_codejams(conn: asyncpg.Connection) -> list[tuple[int, str]]:
    """Fetch all the codejams stored in the database."""
    return await conn.fetch("SELECT jam_id, jam_name FROM jams ORDER BY jam_id DESC")


async def get_codejam_data(conn: asyncpg.Connection, jam_id: int, jam_name: str) -> dict[str, Any]:
    """Gets all the data stored in the database about the specified codejam."""
    codejam = {"id": jam_id, "name": jam_name}

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
        team["id"] = team_id
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
async def get_codejams(request: Request) -> list[dict[str, Any]]:
    """Get all the codejams stored in the database."""
    db_codejams = await fetch_codejams(request.state.db_conn)
    codejams = []

    for jam_id, jam_name in db_codejams:
        codejam = await get_codejam_data(request.state.db_conn, jam_id, jam_name)
        codejams.append(codejam)

    return codejams


@router.get(
    "/{codejam_id}",
    response_model=CodeJamResponse,
    responses={
        404: {
            "description": "CodeJam could not be found."
        }
    }
)
async def get_codejam(request: Request, codejam_id: int) -> dict[str, Any]:
    """Get a specific codejam stored in the database by ID."""
    jam_name = await request.state.db_conn.fetchval(
        "SELECT jam_name FROM jams WHERE jam_id = $1", codejam_id
    )

    if not jam_name:
        raise HTTPException(status_code=404, detail="CodeJam with specified ID could not be found.")

    return await get_codejam_data(request.state.db_conn, codejam_id, jam_name)


@router.post("/", response_model=CodeJamResponse)
async def create_codejam(request: Request, codejam: CodeJam) -> dict[str, Any]:
    """Create a new codejam and get back the one just created."""
    new_jam_id = await request.state.db_conn.fetchval(
        "INSERT INTO jams (jam_name) VALUES ($1) RETURNING jam_id",
        codejam.name,
    )
    for team in codejam.teams:
        new_team_id = await request.state.db_conn.fetchval(
            "INSERT INTO teams (jam_id, team_name) VALUES ($1, $2) RETURNING team_id",
            new_jam_id,
            team.name,
        )
        await request.state.db_conn.executemany(
            "INSERT INTO users (user_id) VALUES ($1) ON CONFLICT DO NOTHING",
            [(user.user_id,) for user in team.users],
        )
        await request.state.db_conn.executemany(
            "INSERT INTO team_has_user (team_id, user_id, is_leader) VALUES ($1, $2, $3)",
            [
                (new_team_id, user.user_id, user.is_leader)
                for user in team.users
            ],
        )

    return await get_codejam_data(request.state.db_conn, new_jam_id, codejam.name)
