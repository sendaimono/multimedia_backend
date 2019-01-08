"""Add column

Revision ID: 654ac3d36ec5
Revises: 
Create Date: 2019-01-08 14:56:26.593296

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '654ac3d36ec5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('login', sa.String(40), nullable=False, unique=True),
        sa.Column('password', sa.String(60), nullable=False),
        sa.Column('username', sa.String(80), nullable=False),
        sa.Column('uuid', sa.String(), nullable=False)
    )


def downgrade():
    op.drop_table('users')
