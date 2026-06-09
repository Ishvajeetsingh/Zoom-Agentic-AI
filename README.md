# Zoom Agentic AI

## Overview

Zoom Agentic AI is an AI-powered meeting transcript processing platform that transforms meeting conversations into assessment-ready multiple-choice questions.

The system processes Zoom transcripts or uploaded transcript files through a multi-stage workflow consisting of transcript parsing, cleaning, semantic chunking, and AI-based question generation using locally hosted Large Language Models.

The platform provides a modern web interface for uploading transcripts, processing Zoom meetings, tracking workflow progress, and viewing generated questions.

---

## Features

### Transcript Processing

* Upload transcript files
* Parse transcript content
* Clean and normalize text
* Speaker normalization
* Semantic chunk generation

### AI Question Generation

* Automatic MCQ generation
* Question validation
* Question persistence
* Dynamic question count generation
* Local LLM inference using Ollama

### Zoom Integration

* Zoom OAuth authentication
* Meeting metadata retrieval
* Recording discovery
* Transcript discovery
* Transcript ingestion workflow

### Dashboard

* Transcript management
* Meeting management
* Processing status tracking
* Generated question viewing

---

## Supported Transcript Formats

Currently supported:

* VTT (Zoom Transcript Files)
* TXT (Zoom Chat Export Files)

Note:

JSON uploads are accepted by the upload endpoint but JSON transcript parsing is not currently implemented.

---

## Technology Stack

### Frontend

* React
* TypeScript
* Vite

### Backend

* FastAPI
* Python

### Database

* PostgreSQL
* SQLAlchemy
* Alembic

### AI

* Ollama
* Qwen3 8B
* Phi3 Mini (Fallback)

---

## Processing Pipeline

### Transcript Upload Workflow

```text
Upload
  ↓
Parse
  ↓
Clean
  ↓
Chunk
  ↓
Generate Questions
  ↓
Persist Questions
```

### Zoom Meeting Workflow

```text
Meeting UUID
      ↓
Zoom Authentication
      ↓
Recording Retrieval
      ↓
Transcript Discovery
      ↓
Download
      ↓
Parse
      ↓
Clean
      ↓
Chunk
      ↓
Generate Questions
      ↓
Persist Questions
```

---

## Installation

### Backend

```bash
cd backend

python -m venv .venv

.venv\Scripts\activate

pip install -e .
```

### Database

Create PostgreSQL database:

```text
zoom_agentic_ai
```

Run migrations:

```bash
alembic upgrade head
```

### Ollama

Install Ollama and pull models:

```bash
ollama pull qwen3:8b
ollama pull phi3:mini
```

Verify:

```bash
ollama list
```

---

## Configuration

Configure:

```text
backend/.env
```

Example:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/zoom_agentic_ai

OLLAMA_BASE_URL=http://localhost:11434

OLLAMA_PRIMARY_MODEL=qwen3:8b

OLLAMA_FALLBACK_MODEL=phi3:mini

ZOOM_ACCOUNT_ID=
ZOOM_CLIENT_ID=
ZOOM_CLIENT_SECRET=
```

---

## Running the Backend

```bash
cd backend

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## Running the Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## Zoom Requirements

For processing a real Zoom meeting:

Required:

* Zoom Account ID
* Zoom Client ID
* Zoom Client Secret
* Meeting UUID

Meeting requirements:

* Cloud Recording Enabled
* Zoom Transcript Generated

Without a transcript file, question generation cannot be performed.

---

## Current Status

Implemented:

* Transcript Upload
* Transcript Parsing
* Transcript Cleaning
* Semantic Chunking
* Question Generation
* Question Persistence
* Zoom Meeting Ingestion
* Dashboard UI

Project Status:

```text
Functional Prototype
```

---

## Repository

GitHub:

https://github.com/Ishvajeetsingh/Zoom-Agentic-AI

---

## Author

Ishvajeet Singh

B.Tech Computer Science and Engineering
