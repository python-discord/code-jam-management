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
