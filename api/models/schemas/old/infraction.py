from enum import Enum

from pydantic import BaseModel


class InfractionType(str, Enum):
    """An enumeration of codejam infraction types."""

    note = "note"
    ban = "ban"
    warning = "warning"


class Infraction(BaseModel):
    """A model representing an infraction."""

    user_id: int
    jam_id: int
    reason: str
    infraction_type: InfractionType


class InfractionResponse(Infraction):
    """Response model representing an infraction."""

    id: int

    class Config:
        """Sets ORM mode to true so that pydantic will validate the objects returned by SQLAlchemy."""

        orm_mode = True
