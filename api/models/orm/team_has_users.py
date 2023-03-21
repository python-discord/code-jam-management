from sqlalchemy import Column, ForeignKey, Table

from api.models.orm.base import Base

team_has_users_table = Table(
    "team_has_users",
    Base.metadata,
    Column("team_id", ForeignKey("teams.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)
