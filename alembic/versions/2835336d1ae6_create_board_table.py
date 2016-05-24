"""create board table

Revision ID: 2835336d1ae6
Revises: cef561b43b1
Create Date: 2016-03-28 16:26:19.377178

"""

# revision identifiers, used by Alembic.
revision = '2835336d1ae6'
down_revision = 'cef561b43b1'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'boards',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer),
        sa.ForeignKeyConstraint(['user_id'],['users.id'], ),
        sa.Column('nickname', sa.String(250), nullable=False),
        sa.Column('xdim', sa.Integer, nullable=False),
        sa.Column('ydim', sa.Integer, nullable=False),
        sa.Column('starting_conditions', sa.String(500), nullable=False),

    )


def downgrade():
    op.drop_table('boards')
