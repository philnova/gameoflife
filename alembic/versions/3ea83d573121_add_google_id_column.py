"""add google id column

Revision ID: 3ea83d573121
Revises: 498a7e1175e3
Create Date: 2016-04-05 13:33:47.141402

"""

# revision identifiers, used by Alembic.
revision = '3ea83d573121'
down_revision = '498a7e1175e3'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('users', sa.Column('google_id', sa.String(200)))


def downgrade():
    op.drop_column('users', 'google_id')
