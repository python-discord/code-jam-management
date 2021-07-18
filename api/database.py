from sqlalchemy import BigInteger, Boolean, Column, Enum, ForeignKey, Integer, Text, PrimaryKeyConstraint
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from api.constants import DATABASE_URL


engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()

Session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class TeamUser(Base):
    """A user who belongs to a team."""

    __tablename__ = "team_has_user"
    __table_args__ = (
        PrimaryKeyConstraint('team_id', 'user_id'),
    )

    team_id = Column(ForeignKey("teams.team_id"), nullable=False)
    user_id = Column(ForeignKey("users.user_id"), nullable=False)
    is_leader = Column(Boolean, nullable=False)

    team = relationship("Team", back_populates="users")
    user = relationship("User", back_populates="teams")


class User(Base):
    """A user who has participated in a code jam."""

    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, autoincrement=False)

    teams = relationship("TeamUser", back_populates="users")


class Jam(Base):
    """A code jam."""

    __tablename__ = "jams"

    jam_id = Column(Integer, primary_key=True, autoincrement=True)
    jam_name = Column(Text, nullable=False)

    teams = relationship("Team", back_populates="jam")
    winners = relationship("Winner", back_populates="jam")
    infractions = relationship("Infraction")


class Team(Base):
    """A team participating in a code jam."""

    __tablename__ = "teams"

    team_id = Column(Integer, primary_key=True, autoincrement=True)
    jam_id = Column(ForeignKey("jams.jam_id"), nullable=False)
    team_name = Column(Text, nullable=False)

    jam = relationship("Jam", back_populates="teams")
    users = relationship("TeamUser", back_populates="team")


class Winner(Base):
    """A user who has won a code jam."""

    __tablename__ = "winners"
    __table_args__ = (
        PrimaryKeyConstraint('jam_id', 'user_id'),
    )

    jam_id = Column(ForeignKey("jams.jam_id"), nullable=False)
    user_id = Column(ForeignKey("users.user_id"), nullable=False)
    first_place = Column(Boolean, nullable=False)

    jam = relationship("Jam", back_populates="winners")


class Infraction(Base):
    """An infraction that was applied to a user."""

    __tablename__ = "infractions"

    infraction_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey("users.user_id"))
    jam_id = Column(ForeignKey("jams.jam_id"))
    infraction_type = Column(Enum("note", "ban", "warning", name="infraction_type"), nullable=False)
    reason = Column(Text, nullable=False)
