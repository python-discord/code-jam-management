from pydantic import BaseModel

from api.models.schemas.v1 import infraction, team, winner


class CodeJamBase(BaseModel):
    """A Base model representing a codejam."""

    name: str
    teams: list[team.Team]
    ongoing: bool = False


class CodeJamCreate(CodeJamBase):
    """The expected fields to create a new Code Jam."""


class CodeJam(CodeJamBase):
    """Response model representing a code jam."""

    id: int
    infractions: list[infraction.Infraction]
    winners: list[winner.Winner]

    class Config:
        """Sets ORM mode to true so that pydantic will validate the objects returned by SQLAlchemy."""

        orm_mode = True
