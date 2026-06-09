"""questions table and question persistence fields

Revision ID: 20260601_0007
Revises: 20260601_0006
Create Date: 2026-06-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260601_0007"
down_revision: str | None = "20260601_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "questions",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("transcript_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("meeting_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=True),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(50), nullable=False),
        sa.Column("options", sa.dialects.postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("correct_answer", sa.String(10), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.String(20), nullable=False),
        sa.Column("is_valid", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_duplicate", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("duplicate_of", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["transcript_id"], ["transcripts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chunk_id"], ["transcript_chunks.chunk_id"], ondelete="SET NULL"),
    )
    op.create_index("ix_questions_transcript_id", "questions", ["transcript_id"])
    op.create_index("ix_questions_meeting_id", "questions", ["meeting_id"])
    op.create_index("ix_questions_chunk_id", "questions", ["chunk_id"])


def downgrade() -> None:
    op.drop_index("ix_questions_chunk_id", table_name="questions")
    op.drop_index("ix_questions_meeting_id", table_name="questions")
    op.drop_index("ix_questions_transcript_id", table_name="questions")
    op.drop_table("questions")
