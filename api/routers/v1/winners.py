from fastapi import APIRouter, HTTPException
from sqlalchemy import func
from sqlalchemy.future import select

from api.models.orm import Jam, Team, User
from api.models.schemas.v1.winner import Winner, WinnerResponse
from api.settings import DBSession

router = APIRouter(prefix="/winners", tags=["winners"])


@router.get(
    "/{jam_id}",
    responses={404: {"description": "The specified codejam could not be found."}},
)
async def get_winners(jam_id: int, session: DBSession) -> list[WinnerResponse]:
    """Get the top ten winners from the specified codejam."""
    jam = await session.execute(select(Jam).where(Jam.jam_id == jam_id))
    jam.unique()

    if not jam.scalars().one_or_none():
        raise HTTPException(404, "Jam with specified ID could not be found")

    winners = await session.execute(select(Team).where(Team.winner))
    winners.unique()
    return winners.scalars().all()


@router.post(
    "/{jam_id}",
    responses={
        400: {"description": "The provided winners list is empty or contains duplicate users."},
        404: {
            "description": "The codejam or one of the users provided could not be found.",
        },
        409: {"description": "One or more users are already a winner in the specified codejam."},
    },
)
async def create_winners(jam_id: int, winners: list[Winner], session: DBSession) -> list[WinnerResponse]:
    """Add the top ten winners to the specified codejam."""
    jam = await session.execute(select(Jam).where(Jam.id == jam_id))
    jam.unique()

    if not jam.scalars().one_or_none():
        raise HTTPException(404, "Jam with specified ID could not be found")

    if not winners:
        raise HTTPException(400, "Winners list is empty.")

    winner_ids = {winner.user_id for winner in winners}

    if len(winner_ids) != len(winners):
        raise HTTPException(400, "The provided users contain one or more duplicates.")

    # Make sure all of the winners are in the user database.
    users = await session.execute(select(User).where(User.id == func.any(winner_ids)))
    users.unique()

    if len(users.scalars().all()) != len(winner_ids):
        raise HTTPException(404, "Some users could not be found in the database.")

    winners_response = []

    for winner in winners:
        db_winner = DbWinner(jam_id=jam_id, user_id=winner.user_id, first_place=winner.first_place)
        winners_response.append(WinnerResponse.from_orm(db_winner))
        session.add(db_winner)

    await session.flush()

    return winners_response
