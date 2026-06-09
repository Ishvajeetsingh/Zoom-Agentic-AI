"""transcript cleaning fields

Revision ID: 20260601_0004
Revises: 20260601_0003
Create Date: 2026-06-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260601_0004"
down_revision: str | None = "20260601_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "transcript_segments",
        sa.Column("cleaned_text", sa.Text(), nullable=True),
    )
    op.add_column(
        "transcripts",
        sa.Column("cleaned_segment_count", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "transcripts",
        sa.Column("cleaned_word_count", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "transcripts",
        sa.Column("cleaning_error", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("transcripts", "cleaning_error")
    op.drop_column("transcripts", "cleaned_word_count")
    op.drop_column("transcripts", "cleaned_segment_count")
    op.drop_column("transcript_segments", "cleaned_text")
