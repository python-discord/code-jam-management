from enum import Enum

from pydantic import BaseModel, Field


class User(BaseModel):
    """A model respresenting a user for a codejam."""

    user_id: int
    is_leader: bool


class Team(BaseModel):
    """A model representing a team for a codejam."""

    name: str
    users: list[User]


class CodeJam(BaseModel):
    """A model representing a codejam."""

    jam_name: str
    teams: list[Team]


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


class Winner(BaseModel):
    """A model representing a codejam winner."""

    user_id: int
    first_place: bool


class TeamResponse(Team):
    """Response model representing a team."""

    team_id: int

    class Config:
        """Sets ORM mode to true so that pydantic will validate the objects returned by SQLAlchemy."""

        orm_mode = True


class InfractionResponse(Infraction):
    """Reponse model representing an infraction."""

    infraction_id: int

    class Config:
        """Sets ORM mode to true so that pydantic will validate the objects returned by SQLAlchemy."""

        orm_mode = True


class ParticipationHistory(BaseModel):
    """A model representing the participathon history of a user in a codejam."""

    jam_id: int
    top_10: bool
    first_place: bool
    team_id: int
    is_leader: bool
    infractions: list[InfractionResponse]

    class Config:
        """Sets ORM mode to true so that pydantic will validate the objects returned by SQLAlchemy."""

        orm_mode = True


class UserResponse(BaseModel):
    """Response model representing a user."""

    user_id: int
    participation_history: list[ParticipationHistory]

    class Config:
        """Sets ORM mode to true so that pydantic will validate the objects returned by SQLAlchemy."""

        orm_mode = True


class CodeJamResponse(CodeJam):
    """Response model representing a code jam."""

    jam_id: int
    teams: list[TeamResponse]
    infractions: list[InfractionResponse]
    winners: list[Winner]

    class Config:
        """Sets ORM mode to true so that pydantic will validate the objects returned by SQLAlchemy."""

        orm_mode = True
