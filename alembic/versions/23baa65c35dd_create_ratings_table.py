"""create ratings table

Revision ID: 23baa65c35dd
Revises: 2835336d1ae6
Create Date: 2016-03-28 16:31:04.098972

"""

# revision identifiers, used by Alembic.
revision = '23baa65c35dd'
down_revision = '2835336d1ae6'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'ratings',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer),
        sa.ForeignKeyConstraint(['user_id'],['users.id'], ),
        sa.Column('board_id', sa.Integer),
        sa.ForeignKeyConstraint(['board_id'],['boards.id'], ),
    )


def downgrade():
    op.drop_table('ratings')
