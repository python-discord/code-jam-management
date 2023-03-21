from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.orm import Team
from api.models.orm.base import Base


class Jam(Base):
    """A code jam."""

    __tablename__ = "jams"

    jam_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(), nullable=False)
    ongoing: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    teams: Mapped[list[Team]] = relationship()
