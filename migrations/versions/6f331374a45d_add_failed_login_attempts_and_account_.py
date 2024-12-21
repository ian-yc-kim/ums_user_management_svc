"""Add failed_login_attempts and account_locked_until to User model

Revision ID: 6f331374a45d
Revises: 352c7619c381
Create Date: 2024-12-21 19:33:43.050551

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f331374a45d'
down_revision: Union[str, None] = '352c7619c381'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer(), nullable=False))
    op.add_column('users', sa.Column('account_locked_until', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'account_locked_until')
    op.drop_column('users', 'failed_login_attempts')
    # ### end Alembic commands ###