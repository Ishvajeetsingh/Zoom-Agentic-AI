"""transcript segments

Revision ID: 20260601_0003
Revises: 20260601_0002
Create Date: 2026-06-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260601_0003"
down_revision: str | None = "20260601_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "transcript_segments",
        sa.Column("segment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("transcript_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("meeting_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_time", sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column("end_time", sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column("speaker", sa.Text(), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["transcript_id"], ["transcripts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("segment_id"),
        sa.UniqueConstraint("transcript_id", "sequence_number", name="uq_transcript_segments_sequence"),
    )
    op.create_index(
        op.f("ix_transcript_segments_meeting_id"),
        "transcript_segments",
        ["meeting_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_transcript_segments_transcript_id"),
        "transcript_segments",
        ["transcript_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_transcript_segments_transcript_id"), table_name="transcript_segments")
    op.drop_index(op.f("ix_transcript_segments_meeting_id"), table_name="transcript_segments")
    op.drop_table("transcript_segments")
