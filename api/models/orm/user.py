from typing import TYPE_CHECKING, Literal

from sqlalchemy import BigInteger, Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.orm.base import Base
from api.models.orm.team_has_users import team_has_users_table

ExperienceLevels = Literal["beginner", "decent", "expierienced", "very_expierienced"]


if TYPE_CHECKING:
    from api.models.orm import Team


class User(Base):
    """A user who has participated in a code jam."""

    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)

    teams: Mapped[list["Team"]] = relationship(
        secondary=team_has_users_table,
        back_populates="users",
    )
    jam_specific_details: Mapped[list["JamSpecificDetail"]] = relationship()


class JamSpecificDetail(Base):
    """Jam specific details that a user fills for each code jam."""

    __tablename__ = "jam_specific_details"

    jam_specific_detail_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.user_id))
    jam_id: Mapped[int] = mapped_column(ForeignKey("jams.jam_id"))
    experience_level_git: Mapped[ExperienceLevels] = mapped_column(
        Enum(*ExperienceLevels.__args__, name="experience_level_git_enum"),
        nullable=False,
    )
    experience_level_python: Mapped[ExperienceLevels] = mapped_column(
        Enum(*ExperienceLevels.__args__, name="experience_level_python_enum"),
        nullable=False,
    )
    time_zone: Mapped[str] = mapped_column(String())
    willing_to_lead: Mapped[bool] = mapped_column(Boolean)

    user: Mapped[User] = relationship(back_populates="jam_specific_details")
