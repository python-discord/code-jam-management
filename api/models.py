from __future__ import annotations

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


class ParticipationHistory(BaseModel):
    """A model representing the participathon history of a user in a codejam."""

    jam_id: int
    top_10: bool
    first_place: bool
    team_id: int
    is_leader: bool
    infractions: list[Infraction]


class UserResponse(BaseModel):
    """Response model representing a user."""

    user_id: int
    participation_history: list[ParticipationHistory]


class TeamResponse(Team):
    """Response model representing a team."""

    id: int


class CodeJamResponse(CodeJam):
    """Response model representing a code jam."""

    id: int
    teams: list[TeamResponse]
    infractions: list[Infraction]
    winners: list[Winner]
