"""workflow generation fields on transcripts

Revision ID: 20260601_0006
Revises: 20260601_0005
Create Date: 2026-06-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260601_0006"
down_revision: str | None = "20260601_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "transcripts",
        sa.Column("question_count", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "transcripts",
        sa.Column("generation_model", sa.String(100), nullable=True),
    )
    op.add_column(
        "transcripts",
        sa.Column("generation_error", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("transcripts", "generation_error")
    op.drop_column("transcripts", "generation_model")
    op.drop_column("transcripts", "question_count")
