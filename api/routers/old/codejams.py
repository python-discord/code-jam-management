from typing import Optional

from fastapi import APIRouter, HTTPException
from sqlalchemy import desc, update
from sqlalchemy.future import select

from api.models import CodeJam, CodeJamResponse
from api.models.orm import Jam, Team, User
from api.settings import DBSession

router = APIRouter(prefix="/codejams", tags=["codejams"])


@router.get("/")
async def get_codejams(session: DBSession) -> list[CodeJamResponse]:
    """Get all the codejams stored in the database."""
    codejams = await session.execute(select(Jam).order_by(desc(Jam.id)))
    codejams.unique()

    return codejams.scalars().all()


@router.get(
    "/{codejam_id}",
    responses={404: {"description": "CodeJam could not be found or there is no ongoing code jam."}},
)
async def get_codejam(codejam_id: int, session: DBSession) -> CodeJamResponse:
    """
    Get a specific codejam stored in the database by ID.

    Passing -1 as the codejam ID will return the ongoing codejam.
    """
    if codejam_id == -1:
        ongoing_jams = (await session.execute(select(Jam).where(Jam.ongoing == True))).unique().scalars().all()

        if not ongoing_jams:
            raise HTTPException(status_code=404, detail="There is no ongoing codejam.")

        # With the current implementation, there should only be one ongoing codejam.
        return ongoing_jams[0]

    jam_result = await session.execute(select(Jam).where(Jam.id == codejam_id))
    jam_result.unique()

    if not (jam := jam_result.scalars().one_or_none()):
        raise HTTPException(status_code=404, detail="CodeJam with specified ID could not be found.")

    return jam


@router.patch("/{codejam_id}", responses={404: {"description": "Code Jam with specified ID does not exist."}})
async def modify_codejam(
    codejam_id: int,
    session: DBSession,
    name: Optional[str] = None,
    ongoing: Optional[bool] = None,
) -> CodeJamResponse:
    """Modify the specified codejam to change its name and/or whether it's the ongoing code jam."""
    codejam = await session.execute(select(Jam).where(Jam.id == codejam_id))
    codejam.unique()

    if not codejam.scalars().one_or_none():
        raise HTTPException(status_code=404, detail="Code Jam with specified ID does not exist.")

    if name is not None:
        await session.execute(update(Jam).where(Jam.id == codejam_id).values(name=name))

    if ongoing is not None:
        # Make sure no other Jams are ongoing, and set the specified codejam to ongoing.
        await session.execute(update(Jam).where(Jam.ongoing == True).values(ongoing=False))
        await session.execute(update(Jam).where(Jam.id == codejam_id).values(ongoing=True))

    jam_result = await session.execute(select(Jam).where(Jam.id == codejam_id))
    jam_result.unique()

    jam = jam_result.scalars().one()

    return jam


@router.post("/")
async def create_codejam(codejam: CodeJam, session: DBSession) -> CodeJamResponse:
    """
    Create a new codejam and get back the one just created.

    If the codejam is ongoing, all other codejams will be set to not be ongoing.
    """
    if codejam.ongoing:
        await session.execute(update(Jam).where(Jam.ongoing == True).values(ongoing=False))

    jam = Jam(name=codejam.name, ongoing=codejam.ongoing)
    session.add(jam)
    # Flush here to receive jam ID
    await session.flush()

    for raw_team in codejam.teams:
        team = Team(
            jam_id=jam.id,
            name=raw_team.name,
            discord_role_id=raw_team.discord_role_id,
            discord_channel_id=raw_team.discord_channel_id,
        )
        session.add(team)
        # Flush here to receive team ID
        await session.flush()

        for raw_user in raw_team.users:
            if (
                not (await session.execute(select(User).where(User.id == raw_user.user_id)))
                .unique()
                .scalars()
                .one_or_none()
            ):
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
