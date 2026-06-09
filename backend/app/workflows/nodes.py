from __future__ import annotations

from app.core.config import Settings, settings
from app.core.logging import get_logger
from app.db.repositories import questions as question_repo
from app.services.question_service import QuestionService
from app.workflows.state import ChunkData, QuestionData, WorkflowState, WorkflowStatus

logger = get_logger(__name__)


def load_chunks_node(state: WorkflowState, *, db_session=None) -> dict:
    transcript_id = state["transcript_id"]

    logger.info(
        "workflow.load_chunks.started",
        extra={"transcript_id": str(transcript_id)},
    )

    if db_session is None:
        return {
            "status": WorkflowStatus.FAILED,
            "error": "No database session provided",
            "current_node": "load_chunks",
        }

    from sqlalchemy import select
    from app.db.models.transcript_chunk import TranscriptChunk

    rows = db_session.scalars(
        select(TranscriptChunk)
        .where(TranscriptChunk.transcript_id == transcript_id)
        .order_by(TranscriptChunk.chunk_index)
    ).all()

    if not rows:
        logger.warning(
            "workflow.load_chunks.no_chunks_found",
            extra={"transcript_id": str(transcript_id)},
        )
        return {
            "status": WorkflowStatus.FAILED,
            "error": f"No chunks found for transcript {transcript_id}",
            "current_node": "load_chunks",
        }

    chunks = [
        ChunkData(
            chunk_id=row.chunk_id,
            chunk_index=row.chunk_index,
            text=row.text,
            word_count=row.word_count,
            speakers=list(row.speakers) if row.speakers else [],
        )
        for row in rows
    ]

    logger.info(
        "workflow.load_chunks.completed",
        extra={
            "transcript_id": str(transcript_id),
            "chunks_loaded": len(chunks),
        },
    )

    return {
        "chunks": chunks,
        "chunks_loaded": len(chunks),
        "status": WorkflowStatus.LOADING_CHUNKS,
        "current_node": "load_chunks",
    }


_GENERATION_MAX_RETRIES = 2
_GENERATION_RETRY_DELAY_SECONDS = 2


def generate_questions_node(
    state: WorkflowState,
    *,
    question_service: QuestionService | None = None,
    config: Settings | None = None,
) -> dict:
    import time

    cfg = config or settings
    transcript_id = state["transcript_id"]
    chunks = state.get("chunks", [])

    logger.info(
        "workflow.generate_questions.started",
        extra={
            "transcript_id": str(transcript_id),
            "chunks_to_process": len(chunks),
        },
    )

    service = question_service or QuestionService(config=cfg)

    all_questions: list[QuestionData] = []
    questions_by_chunk: dict[int, int] = {}
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_duration = 0.0
    model_used: str | None = None

    for chunk in chunks:
        chunk_questions: list[QuestionData] = []
        last_exc: Exception | None = None

        for attempt in range(1, _GENERATION_MAX_RETRIES + 2):
            try:
                result = service.generate_questions_from_chunk(
                    chunk_text=chunk.text,
                    chunk_id=chunk.chunk_id,
                    model=cfg.ollama_primary_model,
                )

                if result.questions:
                    for q in result.questions:
                        chunk_questions.append(
                            QuestionData(
                                question_text=q.question_text,
                                question_type=q.question_type,
                                options=q.options,
                                correct_answer=q.correct_answer,
                                explanation=q.explanation,
                                difficulty=q.difficulty,
                                chunk_id=chunk.chunk_id,
                                chunk_index=chunk.chunk_index,
                            )
                        )

                    if result.total_prompt_tokens is not None:
                        total_prompt_tokens += result.total_prompt_tokens
                    if result.total_completion_tokens is not None:
                        total_completion_tokens += result.total_completion_tokens
                    if result.total_duration_seconds is not None:
                        total_duration += result.total_duration_seconds
                    if model_used is None:
                        model_used = result.model_used
                    last_exc = None
                    break

                logger.warning(
                    "workflow.generate_questions.chunk_zero_questions",
                    extra={
                        "transcript_id": str(transcript_id),
                        "chunk_index": chunk.chunk_index,
                        "attempt": attempt,
                        "max_retries": _GENERATION_MAX_RETRIES,
                    },
                )

            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "workflow.generate_questions.chunk_failed",
                    extra={
                        "transcript_id": str(transcript_id),
                        "chunk_index": chunk.chunk_index,
                        "attempt": attempt,
                        "error": str(exc),
                    },
                )

            if attempt <= _GENERATION_MAX_RETRIES:
                time.sleep(_GENERATION_RETRY_DELAY_SECONDS)

        all_questions.extend(chunk_questions)
        questions_by_chunk[chunk.chunk_index] = len(chunk_questions)

        if chunk_questions:
            logger.info(
                "workflow.generate_questions.chunk_completed",
                extra={
                    "transcript_id": str(transcript_id),
                    "chunk_index": chunk.chunk_index,
                    "questions_from_chunk": len(chunk_questions),
                },
            )
        else:
            logger.error(
                "workflow.generate_questions.chunk_exhausted_retries",
                extra={
                    "transcript_id": str(transcript_id),
                    "chunk_index": chunk.chunk_index,
                    "retries_attempted": _GENERATION_MAX_RETRIES,
                    "last_error": str(last_exc) if last_exc else "zero_questions",
                },
            )

    logger.info(
        "workflow.generate_questions.completed",
        extra={
            "transcript_id": str(transcript_id),
            "total_questions": len(all_questions),
            "chunks_processed": len(questions_by_chunk),
        },
    )

    return {
        "questions_raw": all_questions,
        "questions_generated": len(all_questions),
        "questions_by_chunk": questions_by_chunk,
        "model_used": model_used,
        "total_prompt_tokens": total_prompt_tokens if total_prompt_tokens > 0 else None,
        "total_completion_tokens": total_completion_tokens if total_completion_tokens > 0 else None,
        "total_duration_seconds": total_duration if total_duration > 0 else None,
        "status": WorkflowStatus.GENERATING,
        "current_node": "generate_questions",
    }


def validate_questions_node(state: WorkflowState, *, config: Settings | None = None) -> dict:
    cfg = config or settings
    transcript_id = state["transcript_id"]
    questions_raw = state.get("questions_raw", [])

    logger.info(
        "workflow.validate_questions.started",
        extra={
            "transcript_id": str(transcript_id),
            "questions_to_validate": len(questions_raw),
        },
    )

    valid: list[QuestionData] = []
    invalid: list[QuestionData] = []

    for q in questions_raw:
        errors: list[str] = []

        if not q.question_text or len(q.question_text.strip()) < 10:
            errors.append("question_text too short or empty")

        if not q.options or len(q.options) < 2:
            errors.append("must have at least 2 options")
        elif len(q.options) != 4:
            errors.append(f"expected 4 options, got {len(q.options)}")

        if not q.correct_answer or len(q.correct_answer.strip()) == 0:
            errors.append("correct_answer is empty")
        else:
            answer_letter = q.correct_answer.strip()[0].upper()
            if answer_letter not in "ABCD":
                errors.append(f"correct_answer '{q.correct_answer}' is not A/B/C/D")

        if not q.explanation or len(q.explanation.strip()) < 5:
            errors.append("explanation too short or empty")

        if q.difficulty not in ("easy", "medium", "hard"):
            errors.append(f"invalid difficulty: {q.difficulty}")

        if q.question_type != "mcq":
            errors.append(f"unsupported question_type: {q.question_type}")

        if len(questions_raw) > cfg.question_max_count * 2:
            if q.difficulty not in ("easy", "medium", "hard"):
                errors.append("invalid difficulty for filtering")

        q.validation_passed = len(errors) == 0
        q.validation_errors = errors

        if q.validation_passed:
            valid.append(q)
        else:
            invalid.append(q)

    logger.info(
        "workflow.validate_questions.completed",
        extra={
            "transcript_id": str(transcript_id),
            "valid": len(valid),
            "invalid": len(invalid),
        },
    )

    return {
        "questions_valid": valid,
        "questions_invalid": invalid,
        "questions_validated": len(valid),
        "status": WorkflowStatus.VALIDATING,
        "current_node": "validate_questions",
    }


def deduplicate_questions_node(state: WorkflowState) -> dict:
    from app.workflows.dedup import deduplicate_questions

    transcript_id = state["transcript_id"]
    questions_valid = state.get("questions_valid", [])

    logger.info(
        "workflow.deduplicate.started",
        extra={
            "transcript_id": str(transcript_id),
            "questions_to_dedup": len(questions_valid),
        },
    )

    unique, duplicates_removed = deduplicate_questions(questions_valid)

    logger.info(
        "workflow.deduplicate.completed",
        extra={
            "transcript_id": str(transcript_id),
            "unique_questions": len(unique),
            "duplicates_removed": duplicates_removed,
        },
    )

    return {
        "questions_unique": unique,
        "duplicates_removed": duplicates_removed,
        "status": WorkflowStatus.DEDUPLICATING,
        "current_node": "deduplicate",
    }


def persist_questions_node(state: WorkflowState, *, db_session=None) -> dict:
    transcript_id = state["transcript_id"]
    meeting_id = state.get("meeting_id")
    questions_unique = state.get("questions_unique", [])

    logger.info(
        "workflow.persist_questions.started",
        extra={
            "transcript_id": str(transcript_id),
            "questions_to_persist": len(questions_unique),
        },
    )

    if db_session is None:
        return {
            "status": WorkflowStatus.FAILED,
            "error": "No database session provided for question persistence",
            "current_node": "persist_questions",
        }

    if not questions_unique:
        logger.warning(
            "workflow.persist_questions.no_questions",
            extra={"transcript_id": str(transcript_id)},
        )
        return {
            "questions_persisted": 0,
            "status": WorkflowStatus.PERSISTING,
            "current_node": "persist_questions",
        }

    try:
        persisted_count = question_repo.bulk_insert_questions(
            db_session,
            transcript_id=transcript_id,
            meeting_id=meeting_id,
            questions=questions_unique,
        )
    except Exception as exc:
        logger.exception(
            "workflow.persist_questions.failed",
            extra={
                "transcript_id": str(transcript_id),
                "error": str(exc),
            },
        )
        return {
            "status": WorkflowStatus.FAILED,
            "error": f"Failed to persist questions: {exc}",
            "current_node": "persist_questions",
        }

    logger.info(
        "workflow.persist_questions.completed",
        extra={
            "transcript_id": str(transcript_id),
            "questions_persisted": persisted_count,
        },
    )

    return {
        "questions_persisted": persisted_count,
        "status": WorkflowStatus.PERSISTING,
        "current_node": "persist_questions",
    }


def finalize_node(state: WorkflowState) -> dict:
    transcript_id = state["transcript_id"]
    questions_unique = state.get("questions_unique", [])

    logger.info(
        "workflow.finalize.started",
        extra={
            "transcript_id": str(transcript_id),
            "unique_questions": len(questions_unique),
        },
    )

    total_questions = len(questions_unique)
    questions_persisted = state.get("questions_persisted", 0)

    if total_questions == 0:
        chunks_loaded = state.get("chunks_loaded", 0)
        questions_generated = state.get("questions_generated", 0)
        logger.error(
            "workflow.finalize.zero_questions",
            extra={
                "transcript_id": str(transcript_id),
                "chunks_loaded": chunks_loaded,
                "questions_generated": questions_generated,
            },
        )
        return {
            "status": WorkflowStatus.FAILED,
            "error": (
                f"Question generation produced 0 valid questions "
                f"(chunks_loaded={chunks_loaded}, questions_generated={questions_generated}). "
                f"The LLM may have returned an unexpected response format."
            ),
            "current_node": "finalize",
        }

    logger.info(
        "workflow.finalize.completed",
        extra={
            "transcript_id": str(transcript_id),
            "total_questions": total_questions,
            "questions_persisted": questions_persisted,
            "chunks_loaded": state.get("chunks_loaded", 0),
            "questions_generated": state.get("questions_generated", 0),
            "questions_validated": state.get("questions_validated", 0),
            "duplicates_removed": state.get("duplicates_removed", 0),
            "model_used": state.get("model_used"),
        },
    )

    return {
        "total_questions": total_questions,
        "questions_persisted": questions_persisted,
        "status": WorkflowStatus.COMPLETED,
        "current_node": "finalize",
    }


def handle_failure_node(state: WorkflowState) -> dict:
    logger.error(
        "workflow.failure",
        extra={
            "transcript_id": str(state.get("transcript_id", "")),
            "error": state.get("error"),
            "current_node": state.get("current_node", ""),
        },
    )

    return {
        "status": WorkflowStatus.FAILED,
        "current_node": "handle_failure",
    }
