"""add like column to Rating

Revision ID: 555e3a95692b
Revises: 28cc6d8b4060
Create Date: 2016-04-14 16:52:14.725720

"""

# revision identifiers, used by Alembic.
revision = '555e3a95692b'
down_revision = '28cc6d8b4060'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('ratings', sa.Column('like', sa.Boolean()))


def downgrade():
    op.drop_column('ratings', 'like')
