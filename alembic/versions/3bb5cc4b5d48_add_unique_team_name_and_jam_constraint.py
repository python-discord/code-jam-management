"""add unique team name and jam constraint

Revision ID: 3bb5cc4b5d48
Revises: a2c25c740f2a
Create Date: 2022-07-05 20:42:53.033311

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3bb5cc4b5d48'
down_revision = 'a2c25c740f2a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('team_name_jam_unique', 'teams', [sa.text('lower(name)'), 'jam_id'], unique=True)


def downgrade():
    op.drop_index('team_name_jam_unique', 'teams')
