from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.database import Team
from api.dependencies import get_db_session
from api.models import TeamResponse

router = APIRouter(prefix="/teams", tags=["teams"])


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
    teams = await session.execute(select(Team).where(Team.id == team_id))
    teams.unique()

    if not (team := teams.scalars().one_or_none()):
        raise HTTPException(status_code=404, detail="Team with specified ID could not be found.")

    return team
