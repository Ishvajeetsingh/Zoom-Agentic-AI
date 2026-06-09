"""transcript chunks table and chunking fields

Revision ID: 20260601_0005
Revises: 20260601_0004
Create Date: 2026-06-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260601_0005"
down_revision: str | None = "20260601_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "transcript_chunks",
        sa.Column("chunk_id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("transcript_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("meeting_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("word_count", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Numeric(12, 3), nullable=True),
        sa.Column("end_time", sa.Numeric(12, 3), nullable=True),
        sa.Column("speakers", sa.dialects.postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("segment_ids", sa.dialects.postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("segment_range_start", sa.Integer(), nullable=True),
        sa.Column("segment_range_end", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["transcript_id"], ["transcripts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("transcript_id", "chunk_index", name="uq_transcript_chunks_index"),
    )
    op.create_index("ix_transcript_chunks_transcript_id", "transcript_chunks", ["transcript_id"])
    op.create_index("ix_transcript_chunks_meeting_id", "transcript_chunks", ["meeting_id"])

    op.add_column(
        "transcripts",
        sa.Column("chunk_count", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "transcripts",
        sa.Column("chunking_error", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("transcripts", "chunking_error")
    op.drop_column("transcripts", "chunk_count")
    op.drop_index("ix_transcript_chunks_meeting_id", table_name="transcript_chunks")
    op.drop_index("ix_transcript_chunks_transcript_id", table_name="transcript_chunks")
    op.drop_table("transcript_chunks")
