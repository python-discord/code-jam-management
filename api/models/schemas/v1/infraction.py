from pydantic import BaseModel, validator

from api.models.orm.infraction import InfractionType
from api.models.schemas.utils import discord_ids_must_be_snowflake


class InfractionBase(BaseModel):
    """Base model for all infraction types."""

    user_id: int
    jam_id: int
    reason: str
    infraction_type: InfractionType

    # validators
    _ensure_valid_discord_id = validator("user_id", allow_reuse=True)(discord_ids_must_be_snowflake)


class InfractionCreate(InfractionBase):
    """The expected fields to create a new infraction."""


class Infraction(InfractionBase):
    """A model representing an infraction."""

    id: int

    class Config:
        """Sets ORM mode to true so that pydantic will validate the objects returned by SQLAlchemy."""

        orm_mode = True
