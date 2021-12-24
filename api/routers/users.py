from typing import Any

import asyncpg
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.database import TeamUser, User
from api.dependencies import get_db_session
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


async def get_user_data(session: AsyncSession, user_id: int) -> dict[str, Any]:
    """Get the participation history of the specified user."""
    user: dict[str, Any] = {"id": user_id}
    participation_history = []

    user_teams = await session.execute(select(TeamUser).where(TeamUser.user_id == user_id))
    user_teams.unique()

    for user_team in user_teams.scalars().all():
        top_10 = False
        first_place = False

        for winner in user_team.team.jam.winners:
            if winner.user_id == user_id:
                top_10 = True
                first_place = winner.first_place
                break

        infractions = [infraction for infraction in user_team.team.jam.infractions if infraction.user_id == user_id]

        participation_history.append(
            {
                "jam_id": user_team.team.jam.id, "top_10": top_10, "first_place": first_place,
                "team_id": user_team.team.id, "is_leader": user_team.is_leader, "infractions": infractions
            }
        )

    user["participation_history"] = participation_history

    return user


@router.get("/", response_model=list[UserResponse])
async def get_users(session: AsyncSession = Depends(get_db_session)) -> list[dict[str, Any]]:
    """Get information about all the users stored in the database."""
    users = await session.execute(select(User.id))
    users.unique()

    return [await get_user_data(session, user) for user in users.scalars().all()]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    responses={
        404: {
            "description": "User could not be found."
        }
    }
)
async def get_user(user_id: int, session: AsyncSession = Depends(get_db_session)) -> dict[str, Any]:
    """Get a specific user stored in the database by ID."""
    user = await session.execute(select(User).where(User.id == user_id))
    user.unique()

    if not user.scalars().one_or_none():
        raise HTTPException(status_code=404, detail="User with specified ID could not be found.")

    return await get_user_data(session, user_id)
