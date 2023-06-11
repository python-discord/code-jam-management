from fastapi import APIRouter, HTTPException
from sqlalchemy.future import select

from api.models.orm import Infraction as DbInfraction
from api.models.orm import Jam, User
from api.models.schemas.v1.infraction import Infraction, InfractionCreate
from api.settings import DBSession

router = APIRouter(prefix="/infractions", tags=["infractions"])


@router.get("/")
async def get_infractions(session: DBSession) -> list[Infraction]:
    """Get every infraction stored in the database."""
    infractions = await session.execute(select(DbInfraction))
    infractions.unique()

    return infractions.scalars().all()


@router.get(
    "/{infraction_id}",
    responses={404: {"description": "Infraction could not be found."}},
)
async def get_infraction(infraction_id: int, session: DBSession) -> Infraction:
    """Get a specific infraction stored in the database by ID."""
    infraction_result = await session.execute(select(DbInfraction).where(DbInfraction.infraction_id == infraction_id))
    infraction_result.unique()

    if not (infraction := infraction_result.scalars().one_or_none()):
        raise HTTPException(404, "Infraction with specified ID could not be found.")

    return infraction


@router.post(
    "/",
    responses={404: {"Description": "Jam ID or User ID could not be found."}},
)
async def create_infraction(
    infraction: InfractionCreate,
    session: DBSession,
) -> Infraction:
    """Add an infraction for a user to the database."""
    jam_id = (await session.execute(select(Jam.jam_id).where(Jam.jam_id == infraction.jam_id))).scalars().one_or_none()

    if jam_id is None:
        raise HTTPException(404, "Jam with specified ID could not be found.")

    user_id = (
        (await session.execute(select(User.user_id).where(User.user_id == infraction.user_id))).scalars().one_or_none()
    )

    if user_id is None:
        raise HTTPException(404, "User with specified ID could not be found.")

    infraction = DbInfraction(
        user_id=user_id, jam_id=jam_id, infraction_type=infraction.infraction_type, reason=infraction.reason
    )
    session.add(infraction)
    await session.flush()

    infraction_result = await session.execute(select(DbInfraction).where(DbInfraction.infraction_id == infraction.id))
    infraction_result.unique()

    return infraction_result.scalars().one()
