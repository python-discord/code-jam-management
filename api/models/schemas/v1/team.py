from typing import Optional

from pydantic import BaseModel

from api.models.schemas.v1 import user


class TeamBase(BaseModel):
    """A Base model representing a team for a codejam."""

    name: str
    users: list[user.User]
    discord_role_id: Optional[int] = None
    discord_channel_id: Optional[int] = None


class Team(TeamBase):
    """Response model representing a team."""

    id: int
    jam_id: int

    class Config:
        """Sets ORM mode to true so that pydantic will validate the objects returned by SQLAlchemy."""

        orm_mode = True


class UserTeam(BaseModel):
    """A model representing user and team relationship."""

    user_id: int
    team: Team
    is_leader: bool

    class Config:
        """Sets ORM mode to true so that pydantic will validate the objects returned by SQLAlchemy."""

        orm_mode = True
