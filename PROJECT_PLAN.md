# Project Plan

Project: Agentic AI for Automated Question Generation from Zoom Meeting Transcripts

Source of truth: `docs/PROJECT_SPECIFICATION.docx`, document version 1.0, dated 01 June 2026.

Status: planning complete, waiting for implementation approval.

## 1. Project Goal

Build a local-first system that receives Zoom cloud recording completion events, retrieves English meeting transcripts, preprocesses transcript content, and uses an agentic LangGraph workflow with a local Ollama-hosted Qwen 3 8B model to generate 10 to 20 assessment questions per meeting.

The generated questions must be grounded in transcript evidence, validated for quality, deduplicated, stored in PostgreSQL, exposed through FastAPI routes, and optionally displayed in a React + Vite dashboard.

## 2. Approved Scope

### In Scope

- Zoom cloud recordings with English transcripts in VTT or JSON-derived formats.
- Post-meeting processing triggered by Zoom `recording.completed` webhooks.
- Zoom Server-to-Server OAuth for transcript retrieval.
- Transcript parsing, cleaning, speaker handling, semantic chunking, and metadata enrichment.
- Agentic question generation using LangGraph.
- Local LLM execution using Ollama with Qwen 3 8B as the primary model.
- Fallback model support for Llama 3 8B.
- Generation of 10 to 20 questions per meeting.
- Question types:
  - Multiple Choice
  - Short Answer
  - True/False
  - Fill in the Blank
- Validation, regeneration, deduplication, and final selection.
- PostgreSQL persistence for meetings, transcripts, runs, chunks, questions, metrics, and logs.
- Local file storage for raw transcript files.
- REST API for ingestion, processing, status, and question retrieval.
- Basic React + Vite dashboard for viewing generated questions and metrics.
- Documentation and handover material.

### Out of Scope

- Real-time transcription or live question generation.
- Non-English transcript support in the first phase.
- Direct LMS or quiz-platform integration.
- Full multi-user authentication beyond Zoom OAuth/admin usage.
- Password-protected or on-premises recordings.
- Commercial cloud LLM APIs.

## 3. Architecture Summary

The system will use a modular local-first architecture:

- Backend API: FastAPI
- Database: PostgreSQL
- AI orchestration: LangGraph
- LLM runtime: Ollama
- Primary model: Qwen 3 8B
- Fallback model: Llama 3 8B
- Frontend: React + Vite
- Storage: local filesystem for raw transcript artifacts
- Integration: Zoom REST API and Zoom Webhooks

The main data flow is:

1. Zoom sends `recording.completed` webhook.
2. FastAPI verifies and records the webhook event.
3. Backend retrieves transcript metadata and downloads transcript file.
4. Transcript is stored locally and registered in PostgreSQL.
5. Preprocessing parses, cleans, speaker-normalizes, and chunks the transcript.
6. LangGraph plans question distribution across chunks.
7. Generation nodes create candidate questions.
8. Validation node checks relevance, clarity, completeness, and transcript grounding.
9. Failed questions are regenerated within retry limits.
10. Deduplication removes overlapping questions.
11. Final selector chooses the best 10 to 20 questions.
12. Output formatter stores structured question JSON and metadata.
13. REST API and dashboard expose the results.

## 4. Module Inventory

| Module | Responsibility | Planned Location |
| --- | --- | --- |
| Configuration | Environment loading, settings validation, paths, model names | `backend/app/core` |
| Logging | Structured logs, request IDs, run IDs, processing status | `backend/app/core` |
| Database | SQLAlchemy models, migrations, repositories, session handling | `backend/app/db` |
| Zoom Integration | OAuth token handling, webhook validation, recording metadata, transcript download | `backend/app/integrations/zoom` |
| Transcript Storage | Safe transcript file paths, raw file persistence, checksums | `backend/app/services/storage_service.py` |
| Transcript Parser | VTT parsing, timestamp extraction, speaker/text extraction | `backend/app/services/transcript_parser.py` |
| Transcript Preprocessor | cleaning, speaker fallback labels, chunking, metadata enrichment | `backend/app/services/preprocessing_service.py` |
| LangGraph State | Typed workflow state for transcript chunks, candidates, validation, metrics | `backend/app/agent/state.py` |
| LangGraph Workflow | graph construction, routing, retry loops, final state output | `backend/app/agent/graph.py` |
| Agent Tools | summarize chunk, generate question types, validate, dedupe, select | `backend/app/agent/tools` |
| Prompt Management | prompt templates for planning, generation, validation, refinement | `backend/app/agent/prompts` |
| Ollama Client | local model calls, model fallback, timeouts, output parsing | `backend/app/llm` |
| Question Service | orchestration from transcript to saved questions | `backend/app/services/question_service.py` |
| Processing Jobs | background execution, run status, retry policy | `backend/app/workers` |
| REST API | health, webhooks, meetings, transcripts, processing runs, questions, metrics | `backend/app/api` |
| Frontend API Client | browser-side calls to FastAPI | `frontend/src/api` |
| Dashboard UI | meeting list, run status, question viewer, metrics cards | `frontend/src` |
| Tests | unit, integration, end-to-end, performance, security checks | `tests` |
| Documentation | plan, status, handover, architecture, project specification | root and `docs` |

## 5. Milestones

### Milestone 0: Planning Approval

Deliverables:

- `PROJECT_PLAN.md`
- `PROJECT_STATUS.md`
- `HANDOVER.md`
- `ARCHITECTURE.md`

Exit criteria:

- Mentor/user approves architecture, schema, routes, workflow, and roadmap.
- No implementation code has been generated.

### Milestone 1: Project Foundation

Deliverables:

- Backend package scaffold.
- Frontend scaffold.
- Environment template.
- PostgreSQL migration setup.
- Logging and settings foundation.
- Local storage folders.

Exit criteria:

- FastAPI app starts locally.
- React app starts locally.
- Database connection succeeds.
- Health endpoint works.

### Milestone 2: Transcript Ingestion

Deliverables:

- Zoom OAuth token retrieval.
- Webhook receiver and validation.
- Transcript metadata retrieval.
- VTT transcript download.
- Manual transcript upload path for testing.
- Transcript file persistence and database records.

Exit criteria:

- A sample transcript can be ingested through manual upload.
- A Zoom webhook payload can be accepted and recorded.
- Transcript metadata and raw file path are stored.

### Milestone 3: Preprocessing Pipeline

Deliverables:

- VTT parser.
- Cleaning pipeline.
- Speaker preservation/fallback labeling.
- Topic-aware chunking.
- Chunk metadata persistence.

Exit criteria:

- Sample transcripts are parsed into timestamped segments.
- Chunks respect token limits and timestamp ranges.
- Cleaning avoids destroying important content.

### Milestone 4: Agentic Generation Pipeline

Deliverables:

- Ollama model client.
- LangGraph state model.
- Planning node.
- Question generation nodes.
- Validation/regeneration loop.
- Deduplication node.
- Final selection and formatting.

Exit criteria:

- A transcript produces 10 to 20 grounded questions.
- Questions include type, answer, source segment, difficulty, and confidence.
- Invalid questions are rejected or regenerated.

### Milestone 5: API and Dashboard

Deliverables:

- Meeting, transcript, run, question, and metrics API routes.
- React dashboard for viewing processing status and generated questions.
- Filtering by meeting, question type, difficulty, and confidence.

Exit criteria:

- User can view a meeting and its generated questions from the dashboard.
- JSON output matches the approved schema intent from the specification.

### Milestone 6: Testing, Performance, and Handover

Deliverables:

- Unit tests for parser, cleaning, chunking, validation.
- Integration tests for database and API.
- End-to-end test using sample transcript.
- Performance measurement for 1-hour transcript target.
- Final documentation update.

Exit criteria:

- Target processing time is measured against the approved hardware.
- Security and file validation checks pass.
- Handover docs are complete.

## 6. Implementation Roadmap

### Phase 1: Planning and Approval

- Analyze approved DOCX specification.
- Lock folder structure.
- Lock database schema.
- Lock API route contract.
- Lock LangGraph workflow.
- Obtain user/mentor approval before implementation.

### Phase 2: Backend Base

- Initialize FastAPI application structure.
- Add settings, logging, error handling, database session handling.
- Add Alembic migrations.
- Add health and readiness routes.

### Phase 3: Data Model and Persistence

- Create PostgreSQL schema.
- Implement repository boundaries.
- Add local transcript storage conventions.
- Add status lifecycle for processing runs.

### Phase 4: Zoom and Manual Ingestion

- Implement Zoom OAuth client.
- Implement webhook receiver.
- Implement transcript download.
- Implement manual upload/test ingestion.

### Phase 5: Transcript Processing

- Parse VTT.
- Clean transcript text.
- Preserve speaker/timestamp metadata.
- Chunk by topic and token budget.
- Store transcript chunks.

### Phase 6: LangGraph Agent

- Define graph state.
- Implement planner.
- Implement type-specific question generation.
- Implement validator and retry policy.
- Implement deduplication and final selector.
- Save final output.

### Phase 7: API Completion

- Add routes for meetings, transcripts, runs, questions, metrics, and export.
- Add consistent error responses.
- Add pagination/filtering where useful.

### Phase 8: Frontend Dashboard

- Build dashboard shell.
- Add meeting list.
- Add processing status view.
- Add generated question viewer.
- Add metrics summary.

### Phase 9: Quality Hardening

- Add unit, integration, end-to-end, performance, and security tests.
- Validate with real meeting samples.
- Tune prompts and chunking.
- Document limitations and handover steps.

## 7. Acceptance Criteria

- System accepts a Zoom `recording.completed` event.
- System downloads or ingests a transcript.
- System parses and chunks transcript text with timestamps and speakers.
- System generates 10 to 20 questions per meeting.
- Supported question types are MCQ, short answer, true/false, and fill in the blank.
- Every final question includes grounding evidence from the transcript.
- System stores results in PostgreSQL.
- REST API returns generated questions in structured JSON.
- Dashboard displays meeting outputs and metrics.
- Logs capture processing status, errors, validation outcomes, and execution time.
- Performance target is evaluated: under 2 minutes for a 1-hour transcript on the approved hardware, where feasible with local model constraints.

## 8. Approval Gate

Implementation must not start until this planning package is approved.

Approval requested for:

- Module boundaries.
- Folder structure.
- PostgreSQL schema.
- API route design.
- LangGraph workflow design.
- Implementation roadmap.

