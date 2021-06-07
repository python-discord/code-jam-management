from pydantic import BaseModel


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

    name: str
    teams: list[Team]


class Infraction(BaseModel):
    """A model representing an infraction."""

    infraction_id: int
    user_id: int
    jam_id: int
    infraction_type: str
    reason: str


class Winner(BaseModel):
    """A model representing a codejam winner."""

    user_id: int
    first_place: bool


class TeamResponse(BaseModel):
    """Response model representing a team."""

    id: int
    name: str
    users: list[User]


class CodeJamResponse(BaseModel):
    """Response model representing a code jam."""

    id: int
    name: str
    teams: list[TeamResponse]
    infractions: list[Infraction]
    winners: list[Winner]
