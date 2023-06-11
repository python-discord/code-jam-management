"""New ORM models

Revision ID: 698fc7687b7f
Revises: 3bb5cc4b5d48
Create Date: 2023-03-25 22:25:55.765694

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "698fc7687b7f"
down_revision = "3bb5cc4b5d48"
branch_labels = None
depends_on = None


def upgrade():
    # Primary key renames
    # "DROP CONSTRAINT ... CASCADE" is psql specific, and not supported by alembic. Need to manually call using .execute().

    # infractions_pk isn't referenced by any other tables
    op.execute("ALTER TABLE infractions DROP CONSTRAINT infractions_pk CASCADE")
    op.alter_column("infractions", "id", new_column_name="infraction_id")
    op.create_primary_key("infractions_pk", "infractions", ["infraction_id"])

    # jams_pk is used by infractions, teams & winners
    # winners is being deleted, so don't care about that table
    op.execute("ALTER TABLE jams DROP CONSTRAINT jams_pk CASCADE")
    op.alter_column("jams", "id", new_column_name="jam_id")
    op.create_primary_key("jams_pk", "jams", ["jam_id"])
    # Update foreign key to jams_pk in infractions
    op.alter_column("infractions", "jam_id", new_column_name="issued_in_jam_id", nullable=False)
    op.create_foreign_key(
        op.f("infractions_issued_in_jam_id_jams_fk"), "infractions", "jams", ["issued_in_jam_id"], ["jam_id"]
    )
    # Update foreign key to jams_pk in teams
    op.create_foreign_key(op.f("teams_jam_id_jams_fk"), "teams", "jams", ["jam_id"], ["jam_id"])

    # teams_pk is used by team_has_user
    # team_has_user is being deleted, so don't care about that table
    op.execute("ALTER TABLE teams DROP CONSTRAINT teams_pk CASCADE")
    op.alter_column("teams", "id", new_column_name="team_id")
    op.create_primary_key("teams_pk", "teams", ["team_id"])

    # users_pk is used by infractions, team_has_user & winners
    # team_has_user & winners are being deleted, so don't care about those tables
    op.execute("ALTER TABLE users DROP CONSTRAINT users_pk CASCADE")
    op.alter_column("users", "id", new_column_name="user_id")
    op.create_primary_key("users_pk", "users", ["user_id"])
    op.alter_column("infractions", "user_id", existing_type=sa.BIGINT(), nullable=False)
    op.create_foreign_key(op.f("infractions_user_id_users_fk"), "infractions", "users", ["user_id"], ["user_id"])
    # End primary key renames

    # New columns
    op.alter_column("infractions", "reason", existing_type=sa.TEXT(), type_=sa.String(), existing_nullable=False)

    op.alter_column("jams", "name", existing_type=sa.TEXT(), type_=sa.String(), existing_nullable=False)
    op.alter_column("jams", "ongoing", existing_type=sa.BOOLEAN(), server_default=None, existing_nullable=False)

    op.add_column("teams", sa.Column("leader_id", sa.BigInteger()))
    op.execute(
        "UPDATE teams SET leader_id = tu.user_id from teams t join team_has_user tu USING(team_id) where tu.is_leader"
    )
    op.alter_column("teams", "leader_id", existing_type=sa.Integer(), nullable=False)

    op.add_column("teams", sa.Column("winner", sa.Boolean(), nullable=True))
    op.add_column("teams", sa.Column("first_place_winner", sa.Boolean(), nullable=True))
    op.alter_column("teams", "name", existing_type=sa.TEXT(), type_=sa.String(), existing_nullable=False)
    op.alter_column("teams", "discord_role_id", existing_type=sa.BIGINT())
    op.alter_column("teams", "discord_channel_id", existing_type=sa.BIGINT())
    op.execute(
        "UPDATE teams "
        "SET winner = true, "
        "first_place_winner = w.first_place "
        "from teams t "
        "join winners w USING(jam_id)"
    )

    op.create_foreign_key(op.f("teams_leader_id_users_fk"), "teams", "users", ["leader_id"], ["user_id"])

    op.create_table(
        "jam_specific_details",
        sa.Column("jam_specific_detail_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("jam_id", sa.Integer(), nullable=False),
        sa.Column(
            "experience_level_git",
            sa.Enum("beginner", "decent", "expierienced", "very_expierienced", name="experience_level_git_enum"),
            nullable=False,
        ),
        sa.Column(
            "experience_level_python",
            sa.Enum("beginner", "decent", "expierienced", "very_expierienced", name="experience_level_python_enum"),
            nullable=False,
        ),
        sa.Column("time_zone", sa.String(), nullable=False),
        sa.Column("willing_to_lead", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["jam_id"], ["jams.jam_id"], name=op.f("jam_specific_details_jam_id_jams_fk")),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], name=op.f("jam_specific_details_user_id_users_fk")),
        sa.PrimaryKeyConstraint("jam_specific_detail_id", name=op.f("jam_specific_details_pk")),
    )

    op.create_table(
        "team_has_users",
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["team_id"], ["teams.team_id"], name=op.f("team_has_users_team_id_teams_fk")),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], name=op.f("team_has_users_user_id_users_fk")),
        sa.PrimaryKeyConstraint("team_id", "user_id", name=op.f("team_has_users_pk")),
    )
    op.execute("INSERT INTO team_has_users (team_id, user_id) SELECT team_id, user_id FROM team_has_user")

    op.drop_table("winners")
    op.drop_table("team_has_user")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("id", sa.BIGINT(), autoincrement=False, nullable=False))
    op.drop_column("users", "user_id")
    op.add_column("teams", sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False))
    op.drop_constraint(op.f("teams_jam_id_jams_fk"), "teams", type_="foreignkey")
    op.drop_constraint(op.f("teams_leader_id_users_fk"), "teams", type_="foreignkey")
    op.create_foreign_key("teams_jam_id_jams_fk", "teams", "jams", ["jam_id"], ["id"])
    op.alter_column("teams", "discord_channel_id", existing_type=sa.BIGINT(), nullable=True)
    op.alter_column("teams", "discord_role_id", existing_type=sa.BIGINT(), nullable=True)
    op.alter_column("teams", "name", existing_type=sa.String(), type_=sa.TEXT(), existing_nullable=False)
    op.drop_column("teams", "first_place_winner")
    op.drop_column("teams", "winner")
    op.drop_column("teams", "leader_id")
    op.drop_column("teams", "team_id")
    op.add_column(
        "jams",
        sa.Column(
            "id",
            sa.INTEGER(),
            server_default=sa.text("nextval('jams_id_seq'::regclass)"),
            autoincrement=True,
            nullable=False,
        ),
    )
    op.alter_column(
        "jams", "ongoing", existing_type=sa.BOOLEAN(), server_default=sa.text("false"), existing_nullable=False
    )
    op.alter_column("jams", "name", existing_type=sa.String(), type_=sa.TEXT(), existing_nullable=False)
    op.drop_column("jams", "jam_id")
    op.add_column("infractions", sa.Column("jam_id", sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column("infractions", sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False))
    op.drop_constraint(op.f("infractions_issued_in_jam_id_jams_fk"), "infractions", type_="foreignkey")
    op.drop_constraint(op.f("infractions_user_id_users_fk"), "infractions", type_="foreignkey")
    op.create_foreign_key("infractions_jam_id_jams_fk", "infractions", "jams", ["jam_id"], ["id"])
    op.create_foreign_key("infractions_user_id_users_fk", "infractions", "users", ["user_id"], ["id"])
    op.alter_column("infractions", "reason", existing_type=sa.String(), type_=sa.TEXT(), existing_nullable=False)
    op.alter_column("infractions", "user_id", existing_type=sa.BIGINT(), nullable=True)
    op.drop_column("infractions", "issued_in_jam_id")
    op.drop_column("infractions", "infraction_id")
    op.create_table(
        "team_has_user",
        sa.Column("team_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("is_leader", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], name="team_has_user_team_id_teams_fk"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="team_has_user_user_id_users_fk"),
        sa.PrimaryKeyConstraint("team_id", "user_id", name="team_has_user_pk"),
    )
    op.create_table(
        "winners",
        sa.Column("jam_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("first_place", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(["jam_id"], ["jams.id"], name="winners_jam_id_jams_fk"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="winners_user_id_users_fk"),
        sa.PrimaryKeyConstraint("jam_id", "user_id", name="winners_pk"),
    )
    op.drop_table("team_has_users")
    op.drop_table("jam_specific_details")
    # ### end Alembic commands ###
