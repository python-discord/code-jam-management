from typing import Literal

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from api.models.orm.base import Base

InfractionType = Literal["note", "ban", "warning"]


class Infraction(Base):
    """An infraction that was applied to a user."""

    __tablename__ = "infractions"

    infraction_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    issued_in_jam_id: Mapped[int] = mapped_column(ForeignKey("jams.jam_id"))
    infraction_type: Mapped[InfractionType] = mapped_column(
        Enum(*InfractionType.__args__, name="infraction_type"),
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(String(), nullable=False)
