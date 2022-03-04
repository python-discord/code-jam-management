from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.database import Team, TeamUser, User as DbUser
from api.dependencies import get_db_session
from api.models import TeamResponse, User

router = APIRouter(prefix="/teams", tags=["teams"])


async def ensure_team_exists(team_id: int, session: AsyncSession) -> Team:
    """Ensure that a team with the given ID exists and return it."""
    teams = await session.execute(select(Team).where(Team.id == team_id))
    teams.unique()

    if not (team := teams.scalars().one_or_none()):
        raise HTTPException(status_code=404, detail="Team with specified ID could not be found.")

    return team


async def ensure_user_exists(user_id: int, session: AsyncSession) -> DbUser:
    """Ensure that a user with the given ID exists and return it."""
    users = await session.execute(select(DbUser).where(DbUser.id == user_id))
    users.unique()

    if not (user := users.scalars().one_or_none()):
        raise HTTPException(status_code=404, detail="User with specified ID could not be found.")

    return user


@router.get("/", response_model=list[TeamResponse])
async def get_teams(session: AsyncSession = Depends(get_db_session)) -> list[Team]:
    """Get every code jam team in the database."""
    teams = await session.execute(select(Team))
    teams.unique()

    return teams.scalars().all()


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
    responses={
        404: {
            "description": "Team could not be found."
        }
    }
)
async def get_team(team_id: int, session: AsyncSession = Depends(get_db_session)) -> Team:
    """Get a specific code jam team in the database by ID."""
    return await ensure_team_exists(team_id, session)


@router.get(
    "/{team_id}/users",
    response_model=list[User],
    responses={
        404: {
            "description": "Team could not be found."
        }
    }
)
async def get_team_users(team_id: int, session: AsyncSession = Depends(get_db_session)) -> list[TeamUser]:
    """Get the users of a specific code jam team in the database."""
    await ensure_team_exists(team_id, session)

    team_users = await session.execute(select(TeamUser).where(TeamUser.team_id == team_id))
    team_users.unique()

    return team_users.scalars().all()


@router.post(
    "/{team_id}/users/{user_id}",
    response_model=User,
    responses={
        404: {
            "description": "Team or user could not be found.",
        },
        400: {
            "description": "This user is already on the team."
        }
    }
)
async def add_user_to_team(
    team_id: int, user_id: int, is_leader: bool = False, session: AsyncSession = Depends(get_db_session)
) -> TeamUser:
    """Add a user to a specific code jam team in the database."""
    await ensure_team_exists(team_id, session)
    await ensure_user_exists(user_id, session)

    team_users = await session.execute(
        select(TeamUser).where((TeamUser.team_id == team_id) & (TeamUser.user_id == user_id))
    )
    team_users.unique()

    if team_users.scalars().one_or_none():
        raise HTTPException(status_code=400, detail="This user is already on this team.")

    team_user = TeamUser(team_id=team_id, user_id=user_id, is_leader=is_leader)
    session.add(team_user)
    await session.flush()

    return team_user


@router.delete(
    "/{team_id}/users/{user_id}",
    status_code=204,
    responses={
        404: {
            "description": "Team or user could not be found.",
        },
        400: {
            "description": "This user is not on this team."
        }
    }
)
async def remove_user_from_team(
    team_id: int, user_id: int, session: AsyncSession = Depends(get_db_session)
) -> Response:
    """Remove a user from a specific code jam team in the database."""
    await ensure_team_exists(team_id, session)

    team_users = await session.execute(
        select(TeamUser).where((TeamUser.team_id == team_id) & (TeamUser.user_id == user_id))
    )
    team_users.unique()

    if not (team_user := team_users.scalars().one_or_none()):
        raise HTTPException(status_code=400, detail="This user is not on this team.")

    await session.delete(team_user)
    await session.flush()

    return Response(status_code=204)
