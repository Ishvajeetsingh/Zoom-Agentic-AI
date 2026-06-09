# Handover

Project: Agentic AI for Automated Question Generation from Zoom Meeting Transcripts

Source specification: `docs/PROJECT_SPECIFICATION.docx`

Current state: Zoom integration, transcript retrieval, VTT parsing, transcript cleaning, semantic chunking, and Ollama integration implemented; LangGraph orchestration and AI pipeline completion pending.

## 1. Project Intent

This project will automate assessment question generation from Zoom meeting transcripts. It listens for completed Zoom cloud recordings, downloads the transcript, preprocesses the content, runs an agentic LangGraph workflow using local Ollama models, validates and deduplicates generated questions, stores results in PostgreSQL, and exposes them through a FastAPI API and optional React + Vite dashboard.

## 2. Implemented So Far

- FastAPI backend scaffold and API router.
- Environment configuration through `.env.example`.
- Structured logging setup.
- PostgreSQL connection layer through SQLAlchemy.
- Alembic migration structure.
- Zoom Server-to-Server OAuth token generation.
- Zoom webhook security validation.
- Zoom `endpoint.url_validation` handling.
- Zoom `recording.completed` handling.
- PostgreSQL persistence for meeting metadata, transcript metadata, and webhook events.
- Authenticated streamed transcript downloads.
- Local raw transcript storage under `transcripts/raw/{meeting_id}/`.
- VTT parser for downloaded transcript files.
- Transcript segment persistence.
- Parse trigger endpoint.

## 3. Not Implemented Yet

- LangGraph workflow.
- Question persistence.
- Question validation and deduplication.
- Embeddings.
- Frontend features beyond scaffold placeholders.

## 4. Parsing Workflow

Flow:

1. Transcript retrieval stores a raw `.vtt` file under `transcripts/raw/{meeting_id}/`.
2. Transcript row has `status = downloaded`.
3. `POST /api/v1/transcripts/{transcript_id}/parse` starts parsing.
4. `TranscriptParseService` marks the transcript as `parsing_started`.
5. `VttParser` reads the local `raw_file_path`.
6. Parser extracts:
   - cue sequence order
   - start timestamp in seconds
   - end timestamp in seconds
   - speaker label when present
   - transcript text
7. Parser skips malformed cue blocks, missing timestamps, invalid ranges, empty cues, and exact duplicate cues.
8. Existing segments for the transcript are replaced.
9. New segments are inserted into `transcript_segments`.
10. Transcript row is updated to `parsed` with `segment_count` and `word_count`.
11. If parsing fails, status becomes `parsing_failed` and `parse_error` is stored.

## 5. API Endpoints

Implemented:

- `POST /api/v1/webhooks/zoom`
- `POST /api/v1/transcripts/{transcript_id}/download`
- `POST /api/v1/transcripts/{transcript_id}/parse`
- `POST /api/v1/transcripts/{transcript_id}/clean`
- `POST /api/v1/transcripts/{transcript_id}/chunk`

Still placeholder:

- `POST /api/v1/transcripts/upload`

## 6. Database Migrations

Migrations:

- `backend/alembic/versions/20260601_0001_zoom_integration.py`
- `backend/alembic/versions/20260601_0002_transcript_retrieval.py`
- `backend/alembic/versions/20260601_0003_transcript_segments.py`
- `backend/alembic/versions/20260601_0004_transcript_cleaning.py`
- `backend/alembic/versions/20260601_0005_transcript_chunks.py`

Transcript segment table:

| Column | Purpose |
| --- | --- |
| `segment_id` | Segment primary key |
| `transcript_id` | Parent transcript |
| `meeting_id` | Parent meeting |
| `start_time` | Cue start time in seconds |
| `end_time` | Cue end time in seconds |
| `speaker` | Speaker label |
| `text` | Original parsed transcript text |
| `cleaned_text` | Cleaned transcript text used for downstream processing |
| `sequence_number` | Parser-assigned cue order |

## Semantic Chunking

Implemented:

- TranscriptChunk model
- SemanticChunker service
- ChunkingService orchestration
- Chunk persistence
- Chunk API endpoint

Chunk boundaries are determined using:

- hard word limits
- pause gaps
- speaker changes
- topic-shift phrases
- sentence boundaries

Chunk metadata includes:

- chunk index
- speakers
- segment references
- timestamps
- word counts


## 7. Example Parsed Segment

```json
{
  "segment_id": "generated-uuid",
  "transcript_id": "transcript-uuid",
  "meeting_id": "meeting-uuid",
  "start_time": 5.5,
  "end_time": 8.25,
  "speaker": "Bob",
  "text": "We completed the API integration yesterday.",
  "sequence_number": 2
}
```

## 8. Local Testing Procedure

1. Install backend dependencies, including dev test dependencies.
2. Apply migrations:

```powershell
cd backend
alembic upgrade head
```

3. Start the backend:

```powershell
uvicorn app.main:app --reload
```

4. Download a transcript through the retrieval endpoint.
5. Trigger parsing:

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/api/v1/transcripts/{transcript_id}/parse
```

6. Confirm the transcript row has `status = parsed`.
7. Confirm rows exist in `transcript_segments`.

Parser unit tests:

```powershell
$env:PYTHONPATH="backend"
pytest tests/backend/unit/test_vtt_parser.py
```

## 9. Logging Strategy

Structured log events added:

- `vtt_parser.missing_timestamp`
- `vtt_parser.malformed_timestamp`
- `vtt_parser.empty_cue`
- `vtt_parser.empty_text_after_cleanup`
- `vtt_parser.invalid_time_range`
- `vtt_parser.duplicate_cue_skipped`
- `vtt_parser.completed`
- `transcript_parse.started`
- `transcript_parse.completed`
- `transcript_parse.failed`
- `transcript_parse.api_error`
- `transcript_parse.database_error`

## Ollama Integration

Implemented:

- OllamaApiClient
- Health checking
- Retry/backoff handling
- Model listing
- Model pull support
- JSON generation mode
- Model fallback support

Question service now consumes transcript chunks and generates structured question payloads through Ollama.

No database changes were required.

## 10. Recommended Next Module

Implement LangGraph Workflow.

Recommended sequence:

1. Define workflow state.
2. Create chunk processing node.
3. Create question generation node.
4. Create validation node.
5. Create deduplication node.
6. Create export/output node.
7. Connect workflow to Ollama-powered question generation.

Do not implement embeddings or frontend features until workflow orchestration is reviewed.
