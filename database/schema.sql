-- Logical PostgreSQL schema snapshot for the Zoom Integration module.
-- The executable migration is backend/alembic/versions/20260601_0001_zoom_integration.py.

CREATE TABLE IF NOT EXISTS meetings (
    id uuid PRIMARY KEY,
    source varchar(50) NOT NULL,
    zoom_meeting_id varchar(100),
    zoom_uuid varchar(255) UNIQUE,
    account_id varchar(255),
    host_id varchar(255),
    host_email varchar(255),
    topic text,
    start_time timestamptz,
    timezone varchar(100),
    duration_minutes integer,
    participant_count integer,
    metadata jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS transcripts (
    id uuid PRIMARY KEY,
    meeting_id uuid NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    source_format varchar(50),
    status varchar(50) NOT NULL,
    transcript_filename varchar(255),
    raw_file_path text,
    processed_file_path text,
    zoom_file_id varchar(255),
    zoom_recording_type varchar(100),
    file_type varchar(50),
    file_extension varchar(50),
    file_size_bytes bigint,
    recording_start timestamptz,
    recording_end timestamptz,
    play_url text,
    download_url text,
    language varchar(20),
    segment_count bigint,
    word_count bigint,
    parse_error text,
    download_started_at timestamptz,
    downloaded_at timestamptz,
    download_error text,
    checksum_sha256 varchar(64),
    metadata jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS webhook_events (
    id uuid PRIMARY KEY,
    event_type varchar(150) NOT NULL,
    zoom_event_id varchar(255) UNIQUE,
    request_body_sha256 varchar(64) NOT NULL,
    meeting_id uuid REFERENCES meetings(id) ON DELETE SET NULL,
    payload jsonb NOT NULL,
    headers jsonb NOT NULL,
    received_at timestamptz NOT NULL DEFAULT now(),
    processed_at timestamptz,
    status varchar(50) NOT NULL,
    error_message text
);

CREATE TABLE IF NOT EXISTS transcript_segments (
    segment_id uuid PRIMARY KEY,
    transcript_id uuid NOT NULL REFERENCES transcripts(id) ON DELETE CASCADE,
    meeting_id uuid NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    start_time numeric(12, 3),
    end_time numeric(12, 3),
    speaker text,
    text text NOT NULL,
    sequence_number integer NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_transcript_segments_sequence UNIQUE (transcript_id, sequence_number)
);
