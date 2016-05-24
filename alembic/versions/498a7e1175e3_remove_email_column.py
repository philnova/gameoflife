"""Remove email column

Revision ID: 498a7e1175e3
Revises: 161384c7b438
Create Date: 2016-04-05 13:31:31.600141

"""

# revision identifiers, used by Alembic.
revision = '498a7e1175e3'
down_revision = '161384c7b438'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('users', 'email')


def downgrade():
    op.add_column('users', sa.Column('email', sa.String(200)))
