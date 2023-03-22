from typing import Optional

from pydantic import BaseModel

from api.models.schemas.old import user


class Team(BaseModel):
    """A model representing a team for a codejam."""

    name: str
    users: list[user.User]
    discord_role_id: Optional[int] = None
    discord_channel_id: Optional[int] = None


class TeamResponse(Team):
    """Response model representing a team."""

    id: int
    jam_id: int

    class Config:
        """Sets ORM mode to true so that pydantic will validate the objects returned by SQLAlchemy."""

        orm_mode = True


class UserTeamResponse(BaseModel):
    """Response model representing user and team relationship."""

    user_id: int
    team: TeamResponse
    is_leader: bool

    class Config:
        """Sets ORM mode to true so that pydantic will validate the objects returned by SQLAlchemy."""

        orm_mode = True
