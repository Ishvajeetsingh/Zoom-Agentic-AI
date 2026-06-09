"""Transcript API schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class TranscriptListItem(BaseModel):
    id: uuid.UUID
    meeting_id: uuid.UUID
    source_format: str | None = None
    status: str
    transcript_filename: str | None = None
    file_type: str | None = None
    file_size_bytes: int | None = None
    segment_count: int | None = None
    chunk_count: int | None = None
    question_count: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TranscriptListOut(BaseModel):
    items: list[TranscriptListItem]
    total: int
    offset: int
    limit: int


class TranscriptDetailOut(BaseModel):
    id: uuid.UUID
    meeting_id: uuid.UUID
    source_format: str | None = None
    status: str
    transcript_filename: str | None = None
    raw_file_path: str | None = None
    processed_file_path: str | None = None
    zoom_file_id: str | None = None
    zoom_recording_type: str | None = None
    file_type: str | None = None
    file_extension: str | None = None
    file_size_bytes: int | None = None
    recording_start: datetime | None = None
    recording_end: datetime | None = None
    language: str | None = None
    segment_count: int
    word_count: int | None = None
    cleaned_segment_count: int | None = None
    cleaned_word_count: int | None = None
    chunk_count: int
    question_count: int
    generation_model: str | None = None
    checksum_sha256: str | None = None
    created_at: datetime
    updated_at: datetime
