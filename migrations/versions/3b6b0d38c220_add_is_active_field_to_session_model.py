"""Add is_active field to Session model

Revision ID: 3b6b0d38c220
Revises: 6f331374a45d
Create Date: 2024-12-21 19:46:07.510951

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b6b0d38c220'
down_revision = '6f331374a45d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sessions', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sessions', 'is_active')
    # ### end Alembic commands ###