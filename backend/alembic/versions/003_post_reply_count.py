"""Add post.reply_count for fast hot-sort and list (avoid per-request comment aggregation).

Revision ID: 003
Revises: 002
Create Date: 2025-02-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "posts",
        sa.Column("reply_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.execute("""
        UPDATE posts SET reply_count = (
            SELECT count(*) FROM comments WHERE comments.post_id = posts.id
        )
    """)


def downgrade() -> None:
    op.drop_column("posts", "reply_count")
