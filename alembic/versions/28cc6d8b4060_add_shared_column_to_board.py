"""add shared column to Board

Revision ID: 28cc6d8b4060
Revises: 5ad205d1f5ec
Create Date: 2016-04-14 14:22:10.202530

"""

# revision identifiers, used by Alembic.
revision = '28cc6d8b4060'
down_revision = '5ad205d1f5ec'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('boards', sa.Column('shared', sa.Boolean()))


def downgrade():
    op.drop_column('boards', 'shared')
