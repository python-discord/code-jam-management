from typing import Any, Callable

import asyncpg
from fastapi import FastAPI, HTTPException, Request, Response

from api.constants import DATABASE_POOL
from api.models import UserResponse
from api.routers import codejams

app = FastAPI(docs_url=None, redoc_url="/")

app.include_router(codejams.router)


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


async def fetch_users(pool: asyncpg.Pool) -> list[int]:
    """Fetch all the users stored in the database."""
    return [
        user[0]
        for user in await pool.fetch(
            "SELECT user_id FROM users"
        )
    ]


async def get_user_data(request: Request, id: int) -> dict[str, Any]:
    """Get the participation history of the specified user."""
    user = {"user_id": id}
    participation_history = []

    user_teams = await request.state.db_conn.fetch(
        "SELECT user_id, team_id, is_leader from team_has_user WHERE user_id = $1",
        id
    )

    for user_id, team_id, is_leader in user_teams:
        team = await request.state.db_conn.fetchrow(
            "SELECT jam_id FROM teams WHERE team_id = $1", team_id
        )

        jam_id = team["jam_id"]

        winner = await request.state.db_conn.fetchrow(
            "SELECT first_place FROM winners WHERE jam_id = $1 AND user_id = $2",
            jam_id, user_id
        )

        if winner is not None:
            first_place: bool = winner["first_place"]
            top_10 = True
        else:
            first_place = top_10 = False

        infractions = [
            dict(infraction)
            for infraction in await request.state.db_conn.fetch(
                "SELECT * FROM infractions WHERE jam_id = $1 AND user_id = $2",
                jam_id, user_id
            )
        ]

        participation_history.append(
            dict(
                jam_id=jam_id, top_10=top_10, first_place=first_place,
                team_id=team_id, is_leader=is_leader, infractions=infractions)
        )

    user["participation_history"] = participation_history

    return user


@app.get('/users', response_model=list[UserResponse])
async def get_users(request: Request) -> list[dict[str, Any]]:
    """Get information about all the users stored in the database."""
    users = await fetch_users(request.state.db_conn)

    return [await get_user_data(request, user) for user in users]


@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    responses={
        404: {
            "description": "User could not be found."
        }
    }
)
async def get_user(request: Request, user_id: int) -> dict[str, Any]:
    """Get a specific user stored in the database by ID."""
    db_user = await request.state.db_conn.fetchrow(
        "SELECT * FROM users WHERE user_id = $1", user_id
    )

    if not db_user:
        raise HTTPException(status_code=404, detail="User with specified ID could not be found.")

    return await get_user_data(request, user_id)
