from typing import Any

from fastapi import APIRouter, HTTPException, Request

from api.models import Infraction, InfractionResponse

router = APIRouter(prefix="/infractions", tags=["infractions"])


@router.get("/", response_model=list[InfractionResponse])
async def get_infractions(request: Request) -> list[dict[str, Any]]:
    """Get every the infraction stored in the database."""
    return [
        dict(infraction)
        for infraction in await request.state.db_conn.fetch("SELECT * FROM infractions")
    ]


@router.get(
    "/{infraction_id}",
    response_model=InfractionResponse,
    responses={
        404: {
            "description": "Infraction could not be found."
        }
    }
)
async def get_infraction(request: Request, infraction_id: int) -> dict[str, Any]:
    """Get a specific infraction stored in the database by ID."""
    infraction = await request.state.db_conn.fetchrow(
        "SELECT * FROM infractions WHERE infraction_id = $1", infraction_id
    )

    if not infraction:
        raise HTTPException(404, "Infraction with specified ID could not be found.")

    return dict(infraction)


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
