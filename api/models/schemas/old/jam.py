from pydantic import BaseModel

from api.models.schemas.old import infraction, team, winner


class CodeJam(BaseModel):
    """A model representing a codejam."""

    name: str
    teams: list[team.Team]
    ongoing: bool = False


class CodeJamResponse(CodeJam):
    """Response model representing a code jam."""

    id: int
    teams: list[team.TeamResponse]
    infractions: list[infraction.InfractionResponse]
    winners: list[winner.Winner]

    class Config:
        """Sets ORM mode to true so that pydantic will validate the objects returned by SQLAlchemy."""

        orm_mode = True
