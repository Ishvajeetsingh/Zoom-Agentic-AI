"""zoom integration metadata tables

Revision ID: 20260601_0001
Revises:
Create Date: 2026-06-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260601_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "meetings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("zoom_meeting_id", sa.String(length=100), nullable=True),
        sa.Column("zoom_uuid", sa.String(length=255), nullable=True),
        sa.Column("account_id", sa.String(length=255), nullable=True),
        sa.Column("host_id", sa.String(length=255), nullable=True),
        sa.Column("host_email", sa.String(length=255), nullable=True),
        sa.Column("topic", sa.Text(), nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("timezone", sa.String(length=100), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("participant_count", sa.Integer(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("zoom_uuid"),
    )
    op.create_index(op.f("ix_meetings_account_id"), "meetings", ["account_id"], unique=False)
    op.create_index(op.f("ix_meetings_host_email"), "meetings", ["host_email"], unique=False)
    op.create_index(op.f("ix_meetings_host_id"), "meetings", ["host_id"], unique=False)
    op.create_index(op.f("ix_meetings_start_time"), "meetings", ["start_time"], unique=False)
    op.create_index(op.f("ix_meetings_zoom_meeting_id"), "meetings", ["zoom_meeting_id"], unique=False)
    op.create_index(op.f("ix_meetings_zoom_uuid"), "meetings", ["zoom_uuid"], unique=False)

    op.create_table(
        "transcripts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("meeting_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_format", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("raw_file_path", sa.Text(), nullable=True),
        sa.Column("processed_file_path", sa.Text(), nullable=True),
        sa.Column("zoom_file_id", sa.String(length=255), nullable=True),
        sa.Column("zoom_recording_type", sa.String(length=100), nullable=True),
        sa.Column("file_type", sa.String(length=50), nullable=True),
        sa.Column("file_extension", sa.String(length=50), nullable=True),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("recording_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("recording_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("play_url", sa.Text(), nullable=True),
        sa.Column("download_url", sa.Text(), nullable=True),
        sa.Column("language", sa.String(length=20), nullable=True),
        sa.Column("segment_count", sa.BigInteger(), nullable=True),
        sa.Column("word_count", sa.BigInteger(), nullable=True),
        sa.Column("parse_error", sa.Text(), nullable=True),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_transcripts_checksum_sha256"), "transcripts", ["checksum_sha256"], unique=False)
    op.create_index(op.f("ix_transcripts_meeting_id"), "transcripts", ["meeting_id"], unique=False)
    op.create_index(op.f("ix_transcripts_status"), "transcripts", ["status"], unique=False)
    op.create_index(op.f("ix_transcripts_zoom_file_id"), "transcripts", ["zoom_file_id"], unique=False)
    op.create_index(
        op.f("ix_transcripts_zoom_recording_type"),
        "transcripts",
        ["zoom_recording_type"],
        unique=False,
    )

    op.create_table(
        "webhook_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=150), nullable=False),
        sa.Column("zoom_event_id", sa.String(length=255), nullable=True),
        sa.Column("request_body_sha256", sa.String(length=64), nullable=False),
        sa.Column("meeting_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("headers", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("zoom_event_id"),
    )
    op.create_index(op.f("ix_webhook_events_event_type"), "webhook_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_webhook_events_meeting_id"), "webhook_events", ["meeting_id"], unique=False)
    op.create_index(
        op.f("ix_webhook_events_request_body_sha256"),
        "webhook_events",
        ["request_body_sha256"],
        unique=False,
    )
    op.create_index(op.f("ix_webhook_events_status"), "webhook_events", ["status"], unique=False)
    op.create_index(op.f("ix_webhook_events_zoom_event_id"), "webhook_events", ["zoom_event_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_webhook_events_zoom_event_id"), table_name="webhook_events")
    op.drop_index(op.f("ix_webhook_events_status"), table_name="webhook_events")
    op.drop_index(op.f("ix_webhook_events_request_body_sha256"), table_name="webhook_events")
    op.drop_index(op.f("ix_webhook_events_meeting_id"), table_name="webhook_events")
    op.drop_index(op.f("ix_webhook_events_event_type"), table_name="webhook_events")
    op.drop_table("webhook_events")

    op.drop_index(op.f("ix_transcripts_zoom_recording_type"), table_name="transcripts")
    op.drop_index(op.f("ix_transcripts_zoom_file_id"), table_name="transcripts")
    op.drop_index(op.f("ix_transcripts_status"), table_name="transcripts")
    op.drop_index(op.f("ix_transcripts_meeting_id"), table_name="transcripts")
    op.drop_index(op.f("ix_transcripts_checksum_sha256"), table_name="transcripts")
    op.drop_table("transcripts")

    op.drop_index(op.f("ix_meetings_zoom_uuid"), table_name="meetings")
    op.drop_index(op.f("ix_meetings_zoom_meeting_id"), table_name="meetings")
    op.drop_index(op.f("ix_meetings_start_time"), table_name="meetings")
    op.drop_index(op.f("ix_meetings_host_id"), table_name="meetings")
    op.drop_index(op.f("ix_meetings_host_email"), table_name="meetings")
    op.drop_index(op.f("ix_meetings_account_id"), table_name="meetings")
    op.drop_table("meetings")
