from typing import Any, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from api.constants import DATABASE_POOL
from api.models import CodeJam

app = FastAPI(docs_url="/", redoc_url=None)


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


@app.get("/codejams")
async def get_codejams(request: Request) -> list[dict[str, Any]]:
    """Get all the codejams stored in the database."""
    db_codejams = await request.state.db_conn.fetch("SELECT jam_id, jam_name FROM jams ORDER BY jam_id DESC")
    codejams = []

    for jam_id, jam_name in db_codejams:
        codejam = {"id": jam_id, "name": jam_name}

        db_teams = await request.state.db_conn.fetch(
            "SELECT team_id, team_name FROM teams WHERE jam_id = $1", jam_id
        )

        teams = {}

        for team_id, team_name in db_teams:

            team = {}
            users = []

            db_users = await request.state.db_conn.fetch(
                "SELECT user_id, is_leader from team_has_user WHERE team_id = $1", team_id
            )

            for user_id, is_leader in db_users:
                users.append(dict(user_id=user_id, is_leader=is_leader))

            team["users"] = users
            team["name"] = team_name
            teams[team_id] = team

        codejam["teams"] = teams

        codejam["infractions"] = [
            dict(infraction) for infraction in
            await request.state.db_conn.fetch("SELECT * FROM infractions WHERE jam_id = $1", jam_id)
        ]

        codejam["winners"] = [
            dict(winner) for winner in
            await request.state.db_conn.fetch("SELECT * FROM infractions WHERE jam_id = $1", jam_id)
        ]

        codejams.append(codejam)

    return codejams


@app.get("/codejams/{codejam}")
async def get_codejam(request: Request, codejam: int) -> dict[str, Any]:
    """Get a specific codejam stored in the database by ID."""
    codejams = await get_codejams(request)
    return next(
        (codejam for codejam in codejams if codejam["id"] == codejam),
        JSONResponse(dict(message="The specified codejam was not found."))
    )


@app.post("/codejams")
async def create_codejam(request: Request, codejam: CodeJam) -> Response:
    """Create a new codejam and get back the one just created."""
    new_jam = await request.state.db_conn.fetchrow(
        "INSERT INTO jams (jam_name) VALUES ($1) RETURNING jam_id", codejam.name,
    )
    for team in codejam.teams:
        new_team = await request.state.db_conn.fetchrow(
            "INSERT INTO teams (jam_id, team_name) VALUES ($1, $2) RETURNING team_id",
            new_jam["jam_id"], team.name,
        )
        for user in team.users:
            await request.state.db_conn.execute(
                "INSERT INTO users (user_id) VALUES ($1)", user.user_id
            )
            await request.state.db_conn.execute(
                "INSERT INTO team_has_user (team_id, user_id, is_leader) VALUES ($1, $2, $3)",
                new_team["team_id"], user.user_id, user.is_leader
            )

    return await get_codejam(request, new_jam["jam_id"])
