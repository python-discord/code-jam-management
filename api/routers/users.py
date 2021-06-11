from typing import Any

import asyncpg
from fastapi import APIRouter, HTTPException, Request

from api.models import UserResponse


router = APIRouter(prefix="/users", tags=["users"])


async def fetch_users(conn: asyncpg.Connection) -> list[int]:
    """Fetch all the users stored in the database."""
    return [
        user[0]
        for user in await conn.fetch(
            "SELECT user_id FROM users"
        )
    ]


async def get_user_data(conn: asyncpg.Connection, id: int) -> dict[str, Any]:
    """Get the participation history of the specified user."""
    user: dict[str, Any] = {"user_id": id}
    participation_history = []

    user_teams = await conn.fetch(
        "SELECT user_id, team_id, is_leader from team_has_user WHERE user_id = $1",
        id
    )

    for user_id, team_id, is_leader in user_teams:
        jam_id = await conn.fetchval(
            "SELECT jam_id FROM teams WHERE team_id = $1", team_id
        )

        winner = await conn.fetchrow(
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
            for infraction in await conn.fetch(
                "SELECT * FROM infractions WHERE jam_id = $1 AND user_id = $2",
                jam_id, user_id
            )
        ]

        participation_history.append(
            {
                "jam_id": jam_id, "top_10": top_10, "first_place": first_place,
                "team_id": team_id, "is_leader": is_leader, "infractions": infractions
            }
        )

    user["participation_history"] = participation_history

    return user


@router.get("/", response_model=list[UserResponse])
async def get_users(request: Request) -> list[dict[str, Any]]:
    """Get information about all the users stored in the database."""
    users = await fetch_users(request.state.db_conn)

    return [await get_user_data(request.state.db_conn, user) for user in users]


@router.get(
    "/{user_id}",
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

    return await get_user_data(request.state.db_conn, user_id)
