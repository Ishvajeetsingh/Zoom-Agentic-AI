"""transcript retrieval fields

Revision ID: 20260601_0002
Revises: 20260601_0001
Create Date: 2026-06-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260601_0002"
down_revision: str | None = "20260601_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("transcripts", sa.Column("transcript_filename", sa.String(length=255), nullable=True))
    op.add_column("transcripts", sa.Column("download_started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("transcripts", sa.Column("downloaded_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("transcripts", sa.Column("download_error", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("transcripts", "download_error")
    op.drop_column("transcripts", "downloaded_at")
    op.drop_column("transcripts", "download_started_at")
    op.drop_column("transcripts", "transcript_filename")
