from sqlalchemy import BigInteger, Boolean, Column, Enum, ForeignKey, Index, Integer, PrimaryKeyConstraint, Text, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from api.constants import Config

engine = create_async_engine(Config.DATABASE_URL)
Base = declarative_base()

Session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class TeamUser(Base):
    """A user who belongs to a team."""

    __tablename__ = "team_has_user"
    __table_args__ = (
        PrimaryKeyConstraint('team_id', 'user_id'),
    )

    team_id = Column(ForeignKey("teams.id"), nullable=False)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    is_leader = Column(Boolean, nullable=False)

    team = relationship("Team", back_populates="users", lazy="joined")
    user = relationship("User", back_populates="teams", lazy="joined")


class User(Base):
    """A user who has participated in a code jam."""

    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=False)

    teams = relationship("TeamUser", back_populates="user", lazy="joined")


class Jam(Base):
    """A code jam."""

    __tablename__ = "jams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    ongoing = Column(Boolean, nullable=False, server_default="false")

    teams = relationship("Team", back_populates="jam", lazy="joined")
    winners = relationship("Winner", back_populates="jam", lazy="joined")
    infractions = relationship("Infraction", back_populates="jam", lazy="joined")


class Team(Base):
    """A team participating in a code jam."""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    jam_id = Column(ForeignKey("jams.id"), nullable=False)
    name = Column(Text, nullable=False)
    discord_role_id = Column(BigInteger, nullable=True)
    discord_channel_id = Column(BigInteger, nullable=True)

    jam = relationship("Jam", back_populates="teams", lazy="joined")
    users = relationship("TeamUser", back_populates="team", lazy="joined")

    __table_args__ = (
        Index('team_name_jam_unique', text("lower(name)"), "jam_id", unique=True),
    )


class Winner(Base):
    """A user who has won a code jam."""

    __tablename__ = "winners"
    __table_args__ = (
        PrimaryKeyConstraint('jam_id', 'user_id'),
    )

    jam_id = Column(ForeignKey("jams.id"), nullable=False)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    first_place = Column(Boolean, nullable=False)

    jam = relationship("Jam", back_populates="winners", lazy="joined")


class Infraction(Base):
    """An infraction that was applied to a user."""

    __tablename__ = "infractions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey("users.id"))
    jam_id = Column(ForeignKey("jams.id"))
    infraction_type = Column(Enum("note", "ban", "warning", name="infraction_type"), nullable=False)
    reason = Column(Text, nullable=False)

    user = relationship("User", lazy="joined")
    jam = relationship("Jam", back_populates="infractions", lazy="joined")
