# HANDOVER DOCUMENT

# Zoom Agentic AI

## Project Handover and Operational Guide

---

# Document Information

| Field          | Value                                                             |
| -------------- | ----------------------------------------------------------------- |
| Project Name   | Zoom Agentic AI                                                   |
| Project Type   | AI-Powered Transcript Processing and Question Generation Platform |
| Author         | Ishvajeet Singh                                                   |
| Version        | 1.0                                                               |
| Last Updated   | June 2026                                                         |
| Project Status | Functional Prototype                                              |

---

# Purpose

This document provides all information required to:

* Understand the project architecture
* Configure the development environment
* Run the application
* Process transcript files
* Process Zoom meetings
* Generate questions
* Demonstrate the project
* Troubleshoot common issues

The goal is to enable another developer, faculty member, or evaluator to successfully run and test the system without additional guidance.

---

# Project Overview

Zoom Agentic AI is an intelligent transcript-processing platform that converts meeting conversations into multiple-choice assessment questions using locally hosted Large Language Models (LLMs).

The platform supports:

* Zoom Meeting Processing
* Transcript Upload Processing
* Transcript Parsing
* Transcript Cleaning
* Semantic Chunking
* AI-Based Question Generation
* Database Persistence
* Dashboard Visualization

---

# Technology Stack

## Frontend

* React
* TypeScript
* Vite

---

## Backend

* FastAPI
* Python 3.11+
* SQLAlchemy
* Alembic

---

## Database

* PostgreSQL

---

## AI Layer

* Ollama
* qwen3:8b (Primary)
* phi3:mini (Fallback)

---

# Project Structure

```text
Zoom-Agentic-AI/
│
├── backend/
├── frontend/
├── database/
├── docs/
├── meeting_samples/
├── screenshots/
├── tests/
│
├── README.md
├── ARCHITECTURE.md
├── PROJECT_STATUS.md
├── HANDOVER.md
│
├── .env.example
├── PROJECT_PLAN.md
```

---

# Environment Setup

## Prerequisites

Install:

### Python

Version:

```text
Python 3.11+
```

---

### Node.js

Version:

```text
Node.js 18+
```

---

### PostgreSQL

Version:

```text
PostgreSQL 15+
```

---

### Ollama

Download and install:

https://ollama.com

---

# Database Setup

Create database:

```text
zoom_agentic_ai
```

Example connection string:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/zoom_agentic_ai
```

Run migrations:

```bash
cd backend

alembic upgrade head
```

---

# Ollama Setup

Install required models:

```bash
ollama pull qwen3:8b

ollama pull phi3:mini
```

Verify installation:

```bash
ollama list
```

Expected output:

```text
qwen3:8b
phi3:mini
```

---

# Backend Setup

Navigate to backend directory:

```bash
cd backend
```

Create virtual environment:

```bash
python -m venv .venv
```

Activate environment:

### Windows

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -e .
```

---

# Backend Configuration

Edit:

```text
backend/.env
```

Example:

```env
APP_ENV=development

APP_HOST=127.0.0.1
APP_PORT=8000

DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/zoom_agentic_ai

OLLAMA_BASE_URL=http://localhost:11434

OLLAMA_PRIMARY_MODEL=qwen3:8b
OLLAMA_FALLBACK_MODEL=phi3:mini

ZOOM_ACCOUNT_ID=
ZOOM_CLIENT_ID=
ZOOM_CLIENT_SECRET=
```

---

# Running Backend

Open terminal:

```bash
cd backend
```

Start FastAPI:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Expected:

```text
Application startup complete
```

Backend URL:

```text
http://127.0.0.1:8000
```

Swagger API Documentation:

```text
http://127.0.0.1:8000/docs
```

---

# Frontend Setup

Open a new terminal.

Navigate:

```bash
cd frontend
```

Install packages:

```bash
npm install
```

Run frontend:

```bash
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

---

# Verifying Startup

Backend Verification:

```text
http://127.0.0.1:8000/docs
```

Should display FastAPI Swagger documentation.

Frontend Verification:

```text
http://localhost:5173
```

Should display the dashboard.

---

# Supported Transcript Formats

Currently Supported:

* VTT (Zoom Transcript Files)
* TXT (Zoom Chat Export Files)

Important:

JSON uploads may be accepted by the upload endpoint but JSON transcript parsing is not currently implemented.

---

# Transcript Upload Workflow

## Purpose

Process transcript files directly.

---

## Steps

1. Open Upload Transcript page.
2. Select transcript file.
3. Upload transcript.
4. Start processing.
5. Monitor workflow progress.
6. View generated questions.

---

## Processing Pipeline

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

---

# Zoom Meeting Workflow

## Purpose

Process Zoom meetings directly using Zoom APIs.

---

## Required Credentials

* Zoom Account ID
* Zoom Client ID
* Zoom Client Secret
* Meeting UUID

---

## Zoom Requirements

The target meeting must satisfy:

### Cloud Recording

Enabled

### Transcript Generation

Enabled

Examples:

* Audio Transcript
* Meeting Transcript

Without a transcript file, question generation cannot be performed.

---

## Zoom Processing Flow

```text
Meeting UUID
      ↓
OAuth Authentication
      ↓
Meeting Retrieval
      ↓
Recording Discovery
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

# Frontend Pages

## Dashboard

Displays:

* Transcript counts
* Question counts
* Quick actions
* Navigation shortcuts

---

## Process Meeting

Inputs:

* Zoom Account ID
* Zoom Client ID
* Zoom Client Secret
* Meeting UUID

Output:

* Processing Timeline
* Workflow Status
* Question Generation Results

---

## Upload Transcript

Purpose:

* Upload VTT files
* Upload TXT files

Output:

* Processing Timeline
* Generated Questions

---

# Processing Timeline

Workflow stages:

```text
Received
Download
Parse
Clean
Chunk
Generate
Completed
```

The UI displays the status of each stage.

---

# Question Generation

## AI Models

Primary:

```text
qwen3:8b
```

Fallback:

```text
phi3:mini
```

---

## Question Generation Flow

```text
Transcript Chunk
      ↓
Prompt Construction
      ↓
Ollama
      ↓
Qwen3:8B
      ↓
JSON Output
      ↓
Validation
      ↓
Database Persistence
```

---

# Testing Procedure

## Transcript Upload Test

1. Start backend.
2. Start frontend.
3. Open Upload Transcript page.
4. Upload VTT or TXT transcript.
5. Execute processing pipeline.
6. Verify generated questions.

Expected Result:

Questions should be stored and displayed.

---

## Zoom Meeting Test

1. Configure Zoom credentials.
2. Enter Meeting UUID.
3. Start processing.
4. Verify transcript retrieval.
5. Verify question generation.

Expected Result:

Questions generated from transcript content.

---

# Common Issues

## Uvicorn Not Found

Error:

```text
uvicorn is not recognized
```

Solution:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## Ollama Port Already In Use

Error:

```text
Only one usage of each socket address is normally permitted
```

Reason:

Ollama is already running.

Solution:

Do not launch a second Ollama instance.

---

## No Questions Generated

Possible causes:

### Transcript Contains Mostly Greetings

Examples:

* Thank you sir
* Attendance submitted
* Good afternoon

Result:

Limited meaningful questions.

---

### Transcript Too Small

Result:

Model may generate fewer questions.

---

### Transcript Missing

Result:

Processing cannot continue.

---

## Zoom Processing Failure

Verify:

* Account ID is correct
* Client ID is correct
* Client Secret is correct
* Meeting UUID is correct
* Cloud Recording enabled
* Transcript generated

---

# GitHub Repository

Repository URL:

```text
https://github.com/Ishvajeetsingh/Zoom-Agentic-AI
```

---

# Current Limitations

1. JSON transcript parsing is not implemented.
2. Question quality depends on transcript quality.
3. Chat-heavy transcripts may produce limited questions.
4. Real Zoom testing requires transcript-enabled recordings.

---

# Future Enhancements

Potential future improvements:

* JSON transcript parser
* Google Meet integration
* Microsoft Teams integration
* Export functionality
* Analytics dashboard
* User authentication
* Monitoring dashboard

---

# Handover Checklist

| Item                 | Status    |
| -------------------- | --------- |
| Backend Source Code  | Available |
| Frontend Source Code | Available |
| Database Migrations  | Available |
| Ollama Integration   | Available |
| Zoom Integration     | Available |
| Documentation        | Available |
| GitHub Repository    | Available |
| Demo Workflow        | Available |

---

# Final Handover Status

```text
READY FOR ACADEMIC DEMONSTRATION AND EVALUATION
```

Author:

**Ishvajeet Singh**

B.Tech Computer Science and Engineering

Zoom Agentic AI Project
