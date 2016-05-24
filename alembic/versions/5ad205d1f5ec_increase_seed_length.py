"""increase seed length

Revision ID: 5ad205d1f5ec
Revises: 3ea83d573121
Create Date: 2016-04-07 16:52:57.082576

"""

# revision identifiers, used by Alembic.
revision = '5ad205d1f5ec'
down_revision = '3ea83d573121'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('boards', 'seed')
    op.add_column('boards', sa.Column('seed', sa.String(500000), nullable=False))


def downgrade():
    op.drop_column('boards', 'seed')
    op.add_column('boards', sa.Column('seed', sa.String(1000), nullable=False))
