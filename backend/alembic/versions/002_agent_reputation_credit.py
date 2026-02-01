"""Add agent reputation (REP) and credit (CR) for Reputation Economy.

Revision ID: 002
Revises: 001
Create Date: 2025-02-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("agents", sa.Column("reputation", sa.Float(), nullable=False, server_default="1.0"))
    op.add_column("agents", sa.Column("credit", sa.Float(), nullable=False, server_default="10.0"))


def downgrade() -> None:
    op.drop_column("agents", "credit")
    op.drop_column("agents", "reputation")
