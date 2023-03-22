from pydantic import BaseModel

from api.models.schemas.old import infraction


class User(BaseModel):
    """A model representing a user for a codejam."""

    user_id: int
    is_leader: bool

    class Config:
        """Sets ORM mode to true so that pydantic will validate the objects returned by SQLAlchemy."""

        orm_mode = True


class ParticipationHistory(BaseModel):
    """A model representing the participation history of a user in a codejam."""

    jam_id: int
    top_10: bool
    first_place: bool
    team_id: int
    is_leader: bool
    infractions: list[infraction.InfractionResponse]

    class Config:
        """Sets ORM mode to true so that pydantic will validate the objects returned by SQLAlchemy."""

        orm_mode = True


class UserResponse(BaseModel):
    """Response model representing a user."""

    id: int
    participation_history: list[ParticipationHistory]

    class Config:
        """Sets ORM mode to true so that pydantic will validate the objects returned by SQLAlchemy."""

        orm_mode = True
