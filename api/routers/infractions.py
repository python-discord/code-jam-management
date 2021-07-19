from typing import Any

from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.database import Infraction as DbInfraction
from api.dependencies import get_db_session
from api.models import Infraction, InfractionResponse

router = APIRouter(prefix="/infractions", tags=["infractions"])


@router.get("/", response_model=list[InfractionResponse])
async def get_infractions(session: AsyncSession = Depends(get_db_session)) -> list[dict[str, Any]]:
    """Get every the infraction stored in the database."""
    infractions = await session.execute(select(DbInfraction))
    infractions.unique()

    return infractions.scalars().all()


@router.get(
    "/{infraction_id}",
    response_model=InfractionResponse,
    responses={
        404: {
            "description": "Infraction could not be found."
        }
    }
)
async def get_infraction(infraction_id: int, session: AsyncSession = Depends(get_db_session)) -> dict[str, Any]:
    """Get a specific infraction stored in the database by ID."""
    infraction_result = await session.execute(select(DbInfraction).where(DbInfraction.id == infraction_id))
    infraction_result.unique()

    if not (infraction := infraction_result.scalars().one_or_none()):
        raise HTTPException(404, "Infraction with specified ID could not be found.")

    return infraction


@router.post(
    "/",
    response_model=InfractionResponse,
    responses={
        404: {
            "Description": "Jam ID or User ID could not be found."
        }
    }
)
async def create_infraction(request: Request, infraction: Infraction) -> dict[str, Any]:
    """Add an infraction for a user to the database."""
    jam_id = await request.state.db_conn.fetchval(
        "SELECT jam_id FROM jams WHERE jam_id = $1", infraction.jam_id
    )

    if jam_id is None:
        raise HTTPException(404, "Jam with specified ID could not be found.")

    user_id = await request.state.db_conn.fetchval(
        "SELECT user_id FROM users WHERE user_id = $1", infraction.user_id
    )

    if user_id is None:
        raise HTTPException(404, "User with specified ID could not be found.")

    infraction_id = await request.state.db_conn.fetchval(
        "INSERT INTO infractions (user_id, jam_id, infraction_type, reason)"
        "VALUES ($1, $2, $3, $4) RETURNING infraction_id",
        user_id, jam_id, infraction.infraction_type, infraction.reason
    )

    return await get_infraction(request, infraction_id)
