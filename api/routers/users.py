from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.database import Jam, TeamUser, User
from api.dependencies import get_db_session
from api.models import UserResponse, UserTeamResponse

router = APIRouter(prefix="/users", tags=["users"])


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
                "jam_id": user_team.team.jam.id,
                "top_10": top_10,
                "first_place": first_place,
                "team_id": user_team.team.id,
                "is_leader": user_team.is_leader,
                "infractions": infractions,
            }
        )

    user["participation_history"] = participation_history

    return user


@router.get("/")
async def get_users(session: AsyncSession = Depends(get_db_session)) -> list[UserResponse]:
    """Get information about all the users stored in the database."""
    users = await session.execute(select(User.id))
    users.unique()

    return [await get_user_data(session, user) for user in users.scalars().all()]


@router.get("/{user_id}", responses={404: {"description": "User could not be found."}})
async def get_user(user_id: int, session: AsyncSession = Depends(get_db_session)) -> UserResponse:
    """Get a specific user stored in the database by ID."""
    user = await session.execute(select(User).where(User.id == user_id))
    user.unique()

    if not user.scalars().one_or_none():
        raise HTTPException(status_code=404, detail="User with specified ID could not be found.")

    return await get_user_data(session, user_id)


@router.post("/{user_id}", responses={400: {"description": "User already exists."}})
async def create_user(user_id: int, session: AsyncSession = Depends(get_db_session)) -> UserResponse:
    """Create a new user with the specified ID to the database."""
    user = await session.execute(select(User).where(User.id == user_id))
    user.unique()

    if user.scalars().one_or_none():
        raise HTTPException(status_code=400, detail="User with specified ID already exists.")

    user = User(id=user_id)
    session.add(user)
    await session.flush()

    return await get_user_data(session, user_id)


@router.get(
    "/{user_id}/current_team",
    responses={
        404: {
            "description": (
                "User not found, " "there is no ongoing code jam or " "user isn't participating in current code jam."
            )
        }
    },
)
async def get_current_team(user_id: int, session: AsyncSession = Depends(get_db_session)) -> UserTeamResponse:
    """Get a user's current team information."""
    user = await session.execute(select(User).where(User.id == user_id))
    user.unique()

    if not user.scalars().one_or_none():
        raise HTTPException(status_code=404, detail="User with specified ID could not be found.")

    ongoing_jam = (await session.execute(select(Jam).where(Jam.ongoing == True))).unique().scalars().one_or_none()

    if not ongoing_jam:
        raise HTTPException(status_code=404, detail="There is no ongoing codejam.")

    user_teams = (await session.execute(select(TeamUser).where(TeamUser.user_id == user_id))).unique().scalars().all()

    current_team = None
    for user_team in user_teams:
        if user_team.team.jam_id == ongoing_jam.id:
            current_team = user_team
            break

    if not current_team:
        raise HTTPException(status_code=404, detail="User with specified ID isn't participating in ongoing codejam.")

    return current_team
