"""create users table

Revision ID: cef561b43b1
Revises: 
Create Date: 2016-03-28 16:23:15.848108

"""

# revision identifiers, used by Alembic.
revision = 'cef561b43b1'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('email', sa.String(200)),
    )


def downgrade():
    op.drop_table('users')
