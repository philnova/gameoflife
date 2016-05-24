"""Add seed_string column

Revision ID: 161384c7b438
Revises: 3bb00573b9bb
Create Date: 2016-04-04 18:14:02.220662

"""

# revision identifiers, used by Alembic.
revision = '161384c7b438'
down_revision = '3bb00573b9bb'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('boards', sa.Column('seed', sa.String(1000), nullable=False))
    op.add_column('boards', sa.Column('rules', sa.String(20), nullable=False))


def downgrade():
    op.drop_column('boards', 'seed')
    op.drop_column('boards', 'rules')
