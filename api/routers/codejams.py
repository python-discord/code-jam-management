from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.database import Jam, Team, User, TeamUser
from api.dependencies import get_db_session
from api.models import CodeJam, CodeJamResponse


router = APIRouter(prefix="/codejams", tags=["codejams"])


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
