from pydantic import BaseModel

from api.models.schemas.v1 import infraction


class ParticipationHistory(BaseModel):
    """A model representing the participation history of a user in a codejam."""

    jam_id: int
    top_10: bool
    first_place: bool
    team_id: int
    is_leader: bool
    infractions: list[infraction.Infraction]

    class Config:
        """Sets ORM mode to true so that pydantic will validate the objects returned by SQLAlchemy."""

        orm_mode = True


class UserBase(BaseModel):
    """A Base model representing core data about a user."""

    id: int


class User(UserBase):
    """Response model representing everything about a user."""

    participation_history: list[ParticipationHistory]

    class Config:
        """Sets ORM mode to true so that pydantic will validate the objects returned by SQLAlchemy."""

        orm_mode = True
