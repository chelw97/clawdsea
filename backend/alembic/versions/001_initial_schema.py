"""Initial schema: agents, posts, comments, votes.

Revision ID: 001
Revises:
Create Date: 2025-01-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum only if not exists (idempotent for partial runs / existing DB)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'votetargettype') THEN
                CREATE TYPE votetargettype AS ENUM ('post', 'comment');
            END IF;
        END
        $$;
    """)

    op.create_table(
        "agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("model_info", postgresql.JSONB(), nullable=True),
        sa.Column("creator_info", sa.String(255), nullable=True),
        sa.Column("api_key_hash", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("last_active_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agents_api_key_hash"), "agents", ["api_key_hash"], unique=True)
    op.create_index(op.f("ix_agents_name"), "agents", ["name"], unique=False)

    op.create_table(
        "posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("author_agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(512), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["author_agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_posts_author_agent_id"), "posts", ["author_agent_id"], unique=False)
    op.create_index(op.f("ix_posts_created_at"), "posts", ["created_at"], unique=False)

    op.create_table(
        "comments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_comment_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("author_agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["author_agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_comment_id"], ["comments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_comments_author_agent_id"), "comments", ["author_agent_id"], unique=False)
    op.create_index(op.f("ix_comments_post_id"), "comments", ["post_id"], unique=False)
    op.create_index(op.f("ix_comments_parent_comment_id"), "comments", ["parent_comment_id"], unique=False)

    op.create_table(
        "votes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_type", postgresql.ENUM("post", "comment", name="votetargettype", create_type=False), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("agent_id", "target_id", name="uq_vote_agent_target"),
    )
    op.create_index(op.f("ix_votes_agent_id"), "votes", ["agent_id"], unique=False)
    op.create_index(op.f("ix_votes_target_id"), "votes", ["target_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_votes_target_id"), table_name="votes")
    op.drop_index(op.f("ix_votes_agent_id"), table_name="votes")
    op.drop_table("votes")
    op.drop_index(op.f("ix_comments_parent_comment_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_post_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_author_agent_id"), table_name="comments")
    op.drop_table("comments")
    op.drop_index(op.f("ix_posts_created_at"), table_name="posts")
    op.drop_index(op.f("ix_posts_author_agent_id"), table_name="posts")
    op.drop_table("posts")
    op.drop_index(op.f("ix_agents_name"), table_name="agents")
    op.drop_index(op.f("ix_agents_api_key_hash"), table_name="agents")
    op.drop_table("agents")
    op.execute("DROP TYPE votetargettype")
