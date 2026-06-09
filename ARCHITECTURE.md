# ARCHITECTURE DOCUMENT

# Zoom Agentic AI

## AI-Powered Meeting Transcript Processing and Question Generation System

---

# 1. Introduction

Zoom Agentic AI is a transcript analysis and automated question generation platform that converts meeting transcripts into multiple-choice assessment questions using locally hosted Large Language Models.

The system supports both:

* Zoom meeting transcript ingestion
* Manual transcript file uploads

The application processes transcript content through multiple stages including parsing, cleaning, semantic chunking, and AI-driven question generation.

The architecture follows a modular layered design to ensure maintainability, extensibility, and separation of concerns.

---

# 2. System Objectives

The primary objectives of the system are:

* Automate transcript processing
* Generate educational assessment content
* Support Zoom transcript ingestion
* Support transcript file uploads
* Store generated questions for future use
* Provide a user-friendly dashboard
* Enable local AI inference using Ollama

---

# 3. High-Level Architecture

```text
+--------------------------------------------------+
|                  React Frontend                  |
+--------------------------------------------------+
                     |
                     v
+--------------------------------------------------+
|                  FastAPI Backend                 |
+--------------------------------------------------+
                     |
                     v
+--------------------------------------------------+
|                  Service Layer                   |
+--------------------------------------------------+
| Zoom Service                                     |
| Transcript Service                               |
| Parsing Service                                  |
| Cleaning Service                                 |
| Chunking Service                                 |
| Question Generation Service                      |
+--------------------------------------------------+
                     |
                     v
+--------------------------------------------------+
|                 PostgreSQL Database              |
+--------------------------------------------------+
                     |
                     v
+--------------------------------------------------+
|                    Ollama LLM                    |
+--------------------------------------------------+
| Qwen3:8B                                         |
| Phi3 Mini                                        |
+--------------------------------------------------+
```

---

# 4. Frontend Architecture

The frontend is developed using:

* React
* TypeScript
* Vite

The frontend is responsible for:

* User interaction
* File uploads
* Zoom meeting processing initiation
* Workflow progress visualization
* Displaying generated questions
* Dashboard reporting

---

## Frontend Pages

### Dashboard

Provides:

* Transcript statistics
* Question statistics
* Quick actions
* Navigation shortcuts

---

### Process Meeting

Purpose:

Process Zoom meetings through Zoom integration.

Inputs:

* Zoom Account ID
* Zoom Client ID
* Zoom Client Secret
* Meeting UUID

Output:

* Processing timeline
* Question generation results

---

### Upload Transcript

Purpose:

Upload transcript files for processing.

Supported Formats:

* VTT
* TXT

Note:

JSON uploads are accepted by the API but parsing support is not currently implemented.

---

# 5. Backend Architecture

The backend is implemented using FastAPI.

The backend follows a layered architecture.

```text
API Layer
    |
    v
Service Layer
    |
    v
Repository Layer
    |
    v
Database Layer
```

---

# 6. API Layer

Responsibilities:

* Request validation
* Response generation
* Route management
* Error handling

Major API groups:

```text
/api/v1/zoom
/api/v1/transcripts
/api/v1/meetings
```

---

# 7. Service Layer

The service layer contains the core business logic.

---

## Zoom Ingestion Service

Responsibilities:

* Zoom OAuth authentication
* Meeting metadata retrieval
* Recording discovery
* Transcript discovery
* Meeting registration

---

## Transcript Parse Service

Responsibilities:

* Transcript parsing
* Segment extraction
* Format detection

Supported parsers:

### VttParser

Processes:

* Zoom transcript files
* Standard VTT transcripts

### ZoomChatParser

Processes:

* Zoom chat export TXT files

---

## Transcript Cleaning Service

Responsibilities:

* Text normalization
* Noise removal
* Speaker cleanup
* Segment refinement

---

## Chunking Service

Responsibilities:

* Semantic chunk creation
* Context preservation
* Chunk metadata generation

---

## Question Service

Responsibilities:

* Prompt generation
* LLM communication
* Question parsing
* Question validation
* Question persistence

---

# 8. Database Architecture

The application uses PostgreSQL.

---

## Meetings Table

Stores:

* Meeting UUID
* Meeting topic
* Zoom metadata

---

## Transcripts Table

Stores:

* Transcript metadata
* Processing status
* File information

---

## Transcript Segments Table

Stores:

* Speaker
* Timestamp
* Segment text

---

## Transcript Chunks Table

Stores:

* Chunk text
* Chunk ordering
* Chunk metadata

---

## Questions Table

Stores:

* Question text
* Options
* Correct answer
* Difficulty
* Explanation

---

# 9. Zoom Integration Architecture

Zoom integration uses Server-to-Server OAuth.

Required credentials:

* Zoom Account ID
* Zoom Client ID
* Zoom Client Secret

---

## Zoom Workflow

```text
Meeting UUID
      |
      v
OAuth Authentication
      |
      v
Recording Metadata
      |
      v
Transcript Discovery
      |
      v
Transcript Registration
      |
      v
Processing Pipeline
```

---

## Zoom Requirements

The Zoom meeting must have:

### Cloud Recording Enabled

Required for transcript availability.

### Zoom Transcript Generated

Required for transcript retrieval.

Without a generated transcript file, question generation cannot occur.

---

# 10. Transcript Processing Pipeline

The processing workflow consists of multiple stages.

---

## Stage 1 — Upload or Ingestion

Sources:

* Zoom meeting
* Uploaded transcript file

Output:

* Transcript record

---

## Stage 2 — Parse

Input:

* Raw transcript

Output:

* Transcript segments

---

## Stage 3 — Clean

Input:

* Parsed segments

Output:

* Cleaned segments

---

## Stage 4 — Chunk

Input:

* Cleaned segments

Output:

* Semantic chunks

---

## Stage 5 — Generate

Input:

* Semantic chunks

Output:

* Generated questions

---

## Stage 6 — Persist

Input:

* Generated questions

Output:

* Database records

---

# 11. Question Generation Architecture

Question generation uses Ollama.

Primary model:

```text
qwen3:8b
```

Fallback model:

```text
phi3:mini
```

---

## Generation Flow

```text
Transcript Chunk
      |
      v
Prompt Construction
      |
      v
Ollama API
      |
      v
Qwen3:8B
      |
      v
JSON Response
      |
      v
Validation
      |
      v
Database Persistence
```

---

# 12. Workflow Architecture

The frontend timeline mirrors the backend workflow.

```text
Received
   |
Download
   |
Parse
   |
Clean
   |
Chunk
   |
Generate
   |
Completed
```

Each stage updates transcript status.

---

# 13. Security Architecture

Sensitive information is stored through environment variables.

Examples:

```env
ZOOM_ACCOUNT_ID
ZOOM_CLIENT_ID
ZOOM_CLIENT_SECRET
DATABASE_URL
```

Security principles:

* Configuration isolation
* Environment-based secrets
* No credential storage in source code

---

# 14. Error Handling

The application handles:

### API Errors

* Invalid requests
* Missing fields

### Zoom Errors

* Authentication failures
* Missing recordings
* Missing transcripts

### Processing Errors

* Invalid transcript files
* Parsing failures
* Empty content

### AI Errors

* Model unavailable
* Invalid response format
* Question generation failure

---

# 15. Deployment Architecture

Current deployment environment:

Local development machine.

Components:

```text
Frontend (React)
       |
Backend (FastAPI)
       |
PostgreSQL
       |
Ollama
```

---

# 16. Current Limitations

1. JSON transcript parsing is not implemented.
2. Question quality depends on transcript quality.
3. Chat-heavy transcripts may generate fewer meaningful questions.
4. Real Zoom processing requires transcript-enabled recordings.

---

# 17. Future Enhancements

Potential future improvements:

* JSON transcript parser
* Google Meet integration
* Microsoft Teams integration
* Export functionality
* Analytics dashboard
* User authentication
* Workflow monitoring

---

# 18. Conclusion

Zoom Agentic AI provides a modular architecture for transforming meeting transcripts into assessment-ready questions using local AI models. The system combines Zoom integration, transcript processing, semantic chunking, and automated question generation within a unified workflow while maintaining clear separation between frontend, backend, database, and AI components.
