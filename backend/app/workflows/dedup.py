from __future__ import annotations

import re
from difflib import SequenceMatcher

from app.core.logging import get_logger
from app.workflows.state import QuestionData

logger = get_logger(__name__)

SIMILARITY_THRESHOLD = 0.85


def deduplicate_questions(
    questions: list[QuestionData],
    *,
    similarity_threshold: float = SIMILARITY_THRESHOLD,
) -> tuple[list[QuestionData], int]:
    if not questions:
        return [], 0

    seen_signatures: list[str] = []
    unique: list[QuestionData] = []
    duplicates_removed = 0

    for question in questions:
        signature = _normalize(question.question_text)

        is_duplicate = False
        for existing_sig in seen_signatures:
            if SequenceMatcher(None, signature, existing_sig).ratio() >= similarity_threshold:
                is_duplicate = True
                question.is_duplicate = True
                question.duplicate_of = existing_sig[:80]
                duplicates_removed += 1
                break

        if not is_duplicate:
            seen_signatures.append(signature)
            unique.append(question)

    if duplicates_removed > 0:
        logger.info(
            "dedup.questions_removed",
            extra={
                "duplicates_removed": duplicates_removed,
                "unique_count": len(unique),
                "threshold": similarity_threshold,
            },
        )

    return unique, duplicates_removed


def _normalize(text: str) -> str:
    normalized = text.lower().strip()
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(r"[^\w\s]", "", normalized)
    return normalized
