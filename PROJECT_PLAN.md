# PROJECT PLAN

# Zoom Agentic AI

## Project Planning and Execution Document

---

# Project Information

| Field        | Value                                                             |
| ------------ | ----------------------------------------------------------------- |
| Project Name | Zoom Agentic AI                                                   |
| Project Type | AI-Powered Transcript Processing and Question Generation Platform |
| Author       | Ishvajeet Singh                                                   |
| Version      | 1.0                                                               |
| Duration     | Academic Project                                                  |
| Status       | Completed                                                         |
| Last Updated | June 2026                                                         |

---

# 1. Project Overview

Zoom Agentic AI is an intelligent transcript processing platform designed to transform meeting transcripts into assessment-ready multiple-choice questions using locally hosted Large Language Models.

The project combines transcript processing, semantic understanding, and AI-powered content generation into a unified workflow.

The system supports both Zoom meeting transcripts and manually uploaded transcript files.

---

# 2. Problem Statement

Meetings often contain valuable information, discussions, and learning material. However, extracting educational content manually from lengthy transcripts is time-consuming and inefficient.

There is a need for an automated system capable of:

* Processing meeting transcripts
* Understanding discussion content
* Generating assessment questions
* Storing generated content
* Providing a user-friendly interface

The proposed solution addresses this challenge through Artificial Intelligence and Natural Language Processing techniques.

---

# 3. Project Objectives

## Primary Objectives

* Automate transcript processing
* Generate multiple-choice questions automatically
* Support Zoom meeting transcript ingestion
* Support transcript file uploads
* Store generated questions
* Provide workflow transparency through progress tracking

---

## Secondary Objectives

* Enable local AI inference
* Reduce manual effort
* Improve educational content creation
* Provide a reusable architecture for future meeting platforms

---

# 4. Project Scope

## Included in Scope

### Transcript Processing

* Transcript upload
* Transcript parsing
* Transcript cleaning
* Transcript segmentation

### Question Generation

* MCQ generation
* Question validation
* Question persistence

### Zoom Integration

* OAuth authentication
* Meeting retrieval
* Recording retrieval
* Transcript discovery

### Dashboard

* Processing status tracking
* Workflow visualization
* Question viewing

---

## Excluded from Scope

The following are future enhancements:

* User authentication
* Multi-user collaboration
* Google Meet integration
* Microsoft Teams integration
* Export to PDF
* Export to Word
* Advanced analytics

---

# 5. Functional Requirements

## FR-1 Transcript Upload

The system shall allow users to upload transcript files.

Supported formats:

* VTT
* TXT

---

## FR-2 Zoom Meeting Processing

The system shall allow users to process Zoom meetings using:

* Zoom Account ID
* Zoom Client ID
* Zoom Client Secret
* Meeting UUID

---

## FR-3 Transcript Parsing

The system shall parse transcript content and extract meaningful segments.

---

## FR-4 Transcript Cleaning

The system shall remove unnecessary artifacts and normalize transcript text.

---

## FR-5 Semantic Chunking

The system shall divide transcripts into semantically meaningful chunks.

---

## FR-6 Question Generation

The system shall generate multiple-choice questions from transcript chunks.

---

## FR-7 Question Storage

The system shall store generated questions in PostgreSQL.

---

## FR-8 Progress Tracking

The system shall display workflow progress to users.

---

# 6. Non-Functional Requirements

## Performance

* Fast transcript parsing
* Efficient chunk generation
* Local AI inference

---

## Reliability

* Error handling
* Retry mechanisms
* Workflow validation

---

## Maintainability

* Modular architecture
* Layered design
* Service separation

---

## Usability

* Clean interface
* Professional dashboard
* Easy workflow execution

---

# 7. Technology Selection

## Frontend

### React

Selected because:

* Component-based architecture
* Fast development
* Strong ecosystem

---

### TypeScript

Selected because:

* Type safety
* Better maintainability

---

### Vite

Selected because:

* Fast development server
* Optimized builds

---

## Backend

### FastAPI

Selected because:

* High performance
* Automatic API documentation
* Strong validation support

---

### SQLAlchemy

Selected because:

* ORM support
* Database abstraction

---

### Alembic

Selected because:

* Database migration management

---

## Database

### PostgreSQL

Selected because:

* Reliability
* Scalability
* ACID compliance

---

## AI Layer

### Ollama

Selected because:

* Local deployment
* Privacy
* Open model support

---

### Qwen3:8B

Selected because:

* Strong reasoning capability
* Structured JSON generation
* Good performance on local hardware

---

# 8. System Architecture Plan

The system follows a layered architecture.

```text id="h4zmbv"
Frontend
    |
    v
API Layer
    |
    v
Service Layer
    |
    v
Repository Layer
    |
    v
Database
```

AI services operate independently through Ollama integration.

---

# 9. Development Phases

## Phase 1 – Project Planning

Objectives:

* Requirement gathering
* Architecture design
* Technology selection

Deliverables:

* Project proposal
* Architecture design

Status:

Completed

---

## Phase 2 – Backend Development

Objectives:

* FastAPI setup
* Database integration
* API development

Deliverables:

* Backend APIs
* Database models

Status:

Completed

---

## Phase 3 – Transcript Processing

Objectives:

* Parser implementation
* Cleaning workflow
* Chunking workflow

Deliverables:

* Processing pipeline

Status:

Completed

---

## Phase 4 – AI Integration

Objectives:

* Ollama integration
* Prompt engineering
* Question generation

Deliverables:

* Question generation engine

Status:

Completed

---

## Phase 5 – Frontend Development

Objectives:

* Dashboard creation
* Upload interface
* Workflow visualization

Deliverables:

* User interface

Status:

Completed

---

## Phase 6 – Zoom Integration

Objectives:

* OAuth integration
* Meeting ingestion
* Transcript retrieval

Deliverables:

* Zoom processing workflow

Status:

Implemented

---

## Phase 7 – Testing and Validation

Objectives:

* Workflow testing
* Question generation testing
* End-to-end validation

Deliverables:

* Verified application

Status:

Completed

---

## Phase 8 – Documentation

Objectives:

* README preparation
* Architecture documentation
* Handover preparation

Deliverables:

* Project documentation

Status:

Completed

---

# 10. Workflow Design

## Upload Workflow

```text id="v1q5w5"
Upload
  ↓
Parse
  ↓
Clean
  ↓
Chunk
  ↓
Generate
  ↓
Persist
```

---

## Zoom Workflow

```text id="6wxg8y"
Meeting UUID
      ↓
OAuth Authentication
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
Generate
      ↓
Persist
```

---

# 11. Testing Strategy

## Unit Testing

Purpose:

Validate individual services.

Coverage:

* Parsing
* Cleaning
* Question generation

---

## Integration Testing

Purpose:

Validate complete workflows.

Coverage:

* Upload workflow
* Question generation workflow

---

## Manual Testing

Purpose:

Validate user experience.

Coverage:

* Frontend workflow
* Dashboard functionality

---

# 12. Risk Assessment

| Risk                         | Impact | Mitigation             |
| ---------------------------- | ------ | ---------------------- |
| Invalid Zoom credentials     | Medium | Credential validation  |
| Missing transcript files     | Medium | Error handling         |
| Poor transcript quality      | Medium | Cleaning and chunking  |
| Model response inconsistency | Low    | Validation and retries |
| Database connectivity issues | Low    | Configuration checks   |

---

# 13. Expected Outcomes

The project is expected to:

* Process transcripts automatically
* Generate meaningful MCQs
* Reduce manual effort
* Provide a reusable transcript-analysis framework
* Demonstrate practical AI integration

---

# 14. Deliverables

## Source Code

* Frontend
* Backend
* Database migrations

---

## Documentation

* README.md
* ARCHITECTURE.md
* PROJECT_STATUS.md
* HANDOVER.md
* PROJECT_PLAN.md

---

## Repository

GitHub Repository:

```text id="wgrn35"
https://github.com/Ishvajeetsingh/Zoom-Agentic-AI
```

---

# 15. Final Outcome

The project successfully achieved its primary objectives:

✓ Transcript Processing

✓ Question Generation

✓ Zoom Integration

✓ Dashboard Development

✓ Database Persistence

✓ AI Integration

✓ Documentation

The system is operational and ready for academic demonstration and evaluation.

---

# Project Plan Status

```text id="9e50u6"
PROJECT PLAN EXECUTED SUCCESSFULLY

Project Completion: 95%

Current Status: Ready for Submission
```
