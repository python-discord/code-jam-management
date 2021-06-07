from typing import Any, Callable

from fastapi import FastAPI, HTTPException, Request, Response

from api.constants import DATABASE_POOL
from api.models import CodeJam, CodeJamResponse


app = FastAPI(docs_url=None, redoc_url="/")


@app.on_event("startup")
async def on_startup() -> None:
    """Initialize the DATABASE_POOL on startup."""
    await DATABASE_POOL


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Close the DATABASE_POOL on shutdown."""
    await DATABASE_POOL.close()


@app.middleware("http")
async def setup_data(request: Request, callnext: Callable) -> Response:
    """Get a connection from the pool for every request."""
    try:
        async with DATABASE_POOL.acquire() as connection:
            request.state.db_conn = connection
            return await callnext(request)
    finally:
        request.state.db_conn = None


async def get_codejam_data(request: Request, jam_id: int, jam_name: str) -> dict:
    """Gets all the data stored in the database about the specified codejam."""
    codejam = {"id": jam_id, "name": jam_name}

    db_teams = await request.state.db_conn.fetch(
        "SELECT team_id, team_name FROM teams WHERE jam_id = $1", jam_id
    )

    teams = []

    for team_id, team_name in db_teams:

        team = {}
        users = []

        db_users = await request.state.db_conn.fetch(
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
        for infraction in await request.state.db_conn.fetch(
            "SELECT * FROM infractions WHERE jam_id = $1", jam_id
        )
    ]

    codejam["winners"] = [
        dict(winner)
        for winner in await request.state.db_conn.fetch(
            "SELECT user_id, winner FROM winners WHERE jam_id = $1", jam_id
        )
    ]

    return codejam


@app.get("/codejams", response_model=list[CodeJamResponse])
async def get_codejams(request: Request) -> list[dict[str, Any]]:
    """Get all the codejams stored in the database."""
    db_codejams = await request.state.db_conn.fetch(
        "SELECT jam_id, jam_name FROM jams ORDER BY jam_id DESC"
    )
    codejams = []

    for jam_id, jam_name in db_codejams:
        codejam = await get_codejam_data(request, jam_id, jam_name)
        codejams.append(codejam)

    return codejams


@app.get("/codejams/{codejam_id}", response_model=CodeJamResponse)
async def get_codejam(request: Request, codejam_id: int) -> dict[str, Any]:
    """Get a specific codejam stored in the database by ID."""
    jam_name = await request.state.db_conn.fetchval(
        "SELECT jam_name FROM jams WHERE jam_id = $1", codejam_id
    )

    if not jam_name:
        raise HTTPException(status_code=404, detail="CodeJam with specified ID could not be found.")

    return await get_codejam_data(request, codejam_id, jam_name)


@app.post("/codejams", response_model=CodeJamResponse)
async def create_codejam(request: Request, codejam: CodeJam) -> Response:
    """Create a new codejam and get back the one just created."""
    new_jam = await request.state.db_conn.fetchrow(
        "INSERT INTO jams (jam_name) VALUES ($1) RETURNING jam_id",
        codejam.name,
    )
    for team in codejam.teams:
        new_team = await request.state.db_conn.fetchrow(
            "INSERT INTO teams (jam_id, team_name) VALUES ($1, $2) RETURNING team_id",
            new_jam["jam_id"],
            team.name,
        )
        await request.state.db_conn.executemany(
            "INSERT INTO users (user_id) VALUES ($1) ON CONFLICT DO NOTHING",
            [(user.user_id,) for user in team.users],
        )
        await request.state.db_conn.executemany(
            "INSERT INTO team_has_user (team_id, user_id, is_leader) VALUES ($1, $2, $3)",
            [
                (new_team["team_id"], user.user_id, user.is_leader)
                for user in team.users
            ],
        )

    return await get_codejam(request, new_jam["jam_id"])
