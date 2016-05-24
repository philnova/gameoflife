"""Remove starting conditions column

Revision ID: 3bb00573b9bb
Revises: 23baa65c35dd
Create Date: 2016-04-04 18:11:55.827663

"""

# revision identifiers, used by Alembic.
revision = '3bb00573b9bb'
down_revision = '23baa65c35dd'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('boards', 'starting_conditions')


def downgrade():
    op.add_column('boards', sa.Column('starting_conditions'), sa.String(1000), nullable=False)
