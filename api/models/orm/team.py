from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.orm.base import Base
from api.models.orm.team_has_users import team_has_users_table

if TYPE_CHECKING:
    from api.models.orm import User


class Team(Base):
    """A team participating in a code jam."""

    __tablename__ = "teams"

    team_id: Mapped[int] = mapped_column(primary_key=True)
    jam_id: Mapped[int] = mapped_column(ForeignKey("jams.jam_id"))
    leader_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    name: Mapped[str] = mapped_column(String(), nullable=False)

    # These two fields are nullable to accommodate historic data
    # Routers should enforce tha they are set.
    discord_role_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    discord_channel_id: Mapped[int] = mapped_column(BigInteger, nullable=True)

    winner: Mapped[bool] = mapped_column(Boolean, nullable=True)
    first_place_winner: Mapped[bool] = mapped_column(Boolean, nullable=True)

    users: Mapped[list["User"]] = relationship(
        secondary=team_has_users_table,
        back_populates="teams",
    )
    __table_args__ = (Index("team_name_jam_unique", text("lower(name)"), "jam_id", unique=True),)
