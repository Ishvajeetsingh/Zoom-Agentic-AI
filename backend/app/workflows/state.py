from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, NotRequired, TypedDict


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    LOADING_CHUNKS = "loading_chunks"
    GENERATING = "generating"
    VALIDATING = "validating"
    DEDUPLICATING = "deduplicating"
    PERSISTING = "persisting"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ChunkData:
    chunk_id: uuid.UUID
    chunk_index: int
    text: str
    word_count: int
    speakers: list[str] = field(default_factory=list)


@dataclass
class QuestionData:
    question_text: str
    question_type: str
    options: list[str]
    correct_answer: str
    explanation: str
    difficulty: str
    chunk_id: uuid.UUID | None = None
    chunk_index: int | None = None
    validation_passed: bool = True
    validation_errors: list[str] = field(default_factory=list)
    is_duplicate: bool = False
    duplicate_of: str | None = None


class WorkflowState(TypedDict, total=False):
    transcript_id: uuid.UUID
    meeting_id: uuid.UUID | None
    status: WorkflowStatus
    current_node: str
    error: str | None

    chunks: list[ChunkData]
    chunks_loaded: int

    questions_raw: list[QuestionData]
    questions_generated: int
    questions_by_chunk: dict[int, int]

    questions_valid: list[QuestionData]
    questions_invalid: list[QuestionData]
    questions_validated: int

    questions_unique: list[QuestionData]
    duplicates_removed: int

    questions_persisted: int

    total_questions: int
    model_used: str | None
    total_prompt_tokens: int | None
    total_completion_tokens: int | None
    total_duration_seconds: float | None

    metadata: dict[str, Any]


def make_initial_state(
    transcript_id: uuid.UUID,
    meeting_id: uuid.UUID | None = None,
) -> WorkflowState:
    return WorkflowState(
        transcript_id=transcript_id,
        meeting_id=meeting_id,
        status=WorkflowStatus.PENDING,
        current_node="",
        error=None,
        chunks=[],
        chunks_loaded=0,
        questions_raw=[],
        questions_generated=0,
        questions_by_chunk={},
        questions_valid=[],
        questions_invalid=[],
        questions_validated=0,
        questions_unique=[],
        duplicates_removed=0,
        questions_persisted=0,
        total_questions=0,
        model_used=None,
        total_prompt_tokens=None,
        total_completion_tokens=None,
        total_duration_seconds=None,
        metadata={},
    )


def state_summary(state: WorkflowState) -> dict[str, Any]:
    return {
        "transcript_id": str(state.get("transcript_id", "")),
        "meeting_id": str(state["meeting_id"]) if state.get("meeting_id") else None,
        "status": state.get("status", WorkflowStatus.PENDING).value
        if isinstance(state.get("status"), WorkflowStatus)
        else state.get("status"),
        "current_node": state.get("current_node", ""),
        "error": state.get("error"),
        "chunks_loaded": state.get("chunks_loaded", 0),
        "questions_generated": state.get("questions_generated", 0),
        "questions_validated": state.get("questions_validated", 0),
        "duplicates_removed": state.get("duplicates_removed", 0),
        "questions_persisted": state.get("questions_persisted", 0),
        "total_questions": state.get("total_questions", 0),
        "model_used": state.get("model_used"),
        "total_prompt_tokens": state.get("total_prompt_tokens"),
        "total_completion_tokens": state.get("total_completion_tokens"),
        "total_duration_seconds": state.get("total_duration_seconds"),
    }
