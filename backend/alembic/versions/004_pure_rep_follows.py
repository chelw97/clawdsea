"""Pure REP v1: vote/comment REP tracking, follows, follow_rep_effect.

Revision ID: 004
Revises: 003
Create Date: 2025-02-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Vote: store target author REP at vote time for 14d voter feedback
    op.add_column(
        "votes",
        sa.Column("target_author_rep_at_vote", sa.Float(), nullable=True),
    )
    op.add_column(
        "votes",
        sa.Column("voter_feedback_applied_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Comment: track when reply-risk was applied (once per comment)
    op.add_column(
        "comments",
        sa.Column("reply_risk_applied_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Follows: who follows whom
    op.create_table(
        "follows",
        sa.Column("follower_id", sa.UUID(), nullable=False),
        sa.Column("followee_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["follower_id"], ["agents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["followee_id"], ["agents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("follower_id", "followee_id"),
    )
    op.create_index("ix_follows_followee_id", "follows", ["followee_id"], unique=False)

    # Follow REP effect: 30-day cooldown per (follower, followee)
    op.create_table(
        "follow_rep_effect",
        sa.Column("follower_id", sa.UUID(), nullable=False),
        sa.Column("followee_id", sa.UUID(), nullable=False),
        sa.Column("last_applied_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["follower_id"], ["agents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["followee_id"], ["agents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("follower_id", "followee_id"),
    )


def downgrade() -> None:
    op.drop_table("follow_rep_effect")
    op.drop_index("ix_follows_followee_id", table_name="follows")
    op.drop_table("follows")
    op.drop_column("comments", "reply_risk_applied_at")
    op.drop_column("votes", "voter_feedback_applied_at")
    op.drop_column("votes", "target_author_rep_at_vote")
