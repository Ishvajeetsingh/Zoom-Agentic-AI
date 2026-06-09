import uuid
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.logging import get_logger
from app.db.models.transcript import Transcript
from app.db.models.transcript_chunk import TranscriptChunk
from app.db.models.transcript_segment import TranscriptSegment
from app.db.repositories import transcripts as transcript_repo
from app.services.semantic_chunker import SemanticChunker

logger = get_logger(__name__)


class ChunkingError(AppError):
    """Raised when transcript chunking cannot be completed."""


@dataclass(frozen=True)
class ChunkingResult:
    transcript_id: uuid.UUID
    meeting_id: uuid.UUID
    status: str
    total_chunks: int
    total_words: int
    segments_merged: int


class ChunkingService:
    def __init__(
        self,
        db: Session,
        chunker: SemanticChunker | None = None,
    ) -> None:
        self.db = db
        self.chunker = chunker or SemanticChunker()

    def chunk_transcript(self, transcript_id: uuid.UUID) -> ChunkingResult:
        transcript = transcript_repo.get_by_id(self.db, transcript_id)
        if transcript is None:
            raise ChunkingError(f"Transcript not found: {transcript_id}")

        if transcript.status not in {"cleaned", "chunking_failed"}:
            raise ChunkingError(
                f"Transcript must be cleaned before chunking; current status is {transcript.status}"
            )

        transcript_repo.mark_chunking_started(self.db, transcript)
        self.db.commit()

        logger.info(
            "chunking.started",
            extra={
                "transcript_id": str(transcript.id),
                "meeting_id": str(transcript.meeting_id),
            },
        )

        try:
            segments = self._load_segments(transcript)
            if not segments:
                raise ChunkingError(f"No segments found for transcript {transcript_id}")

            chunking_result = self.chunker.chunk(segments)
            if not chunking_result.chunks:
                raise ChunkingError(f"Chunker produced no chunks for transcript {transcript_id}")

            self._persist_chunks(transcript, chunking_result.chunks)

            transcript_repo.mark_chunked(
                self.db,
                transcript,
                chunk_count=chunking_result.total_chunks,
            )
            self.db.commit()

        except ChunkingError:
            self.db.rollback()
            transcript = transcript_repo.get_by_id(self.db, transcript_id)
            if transcript is not None:
                transcript_repo.mark_chunking_failed(
                    self.db, transcript, "Chunking produced no output"
                )
                self.db.commit()
            raise

        except Exception as exc:
            self.db.rollback()
            transcript = transcript_repo.get_by_id(self.db, transcript_id)
            if transcript is not None:
                transcript_repo.mark_chunking_failed(self.db, transcript, str(exc))
                self.db.commit()
            logger.exception(
                "chunking.failed",
                extra={
                    "transcript_id": str(transcript_id),
                    "error": str(exc),
                },
            )
            raise ChunkingError(str(exc)) from exc

        logger.info(
            "chunking.completed",
            extra={
                "transcript_id": str(transcript.id),
                "meeting_id": str(transcript.meeting_id),
                "total_chunks": chunking_result.total_chunks,
                "total_words": chunking_result.total_words,
                "segments_merged": chunking_result.segments_merged,
            },
        )

        return ChunkingResult(
            transcript_id=transcript.id,
            meeting_id=transcript.meeting_id,
            status=transcript.status,
            total_chunks=chunking_result.total_chunks,
            total_words=chunking_result.total_words,
            segments_merged=chunking_result.segments_merged,
        )

    def _load_segments(self, transcript: Transcript) -> list[dict]:
        rows = self.db.scalars(
            select(TranscriptSegment)
            .where(TranscriptSegment.transcript_id == transcript.id)
            .order_by(TranscriptSegment.sequence_number)
        ).all()

        return [
            {
                "segment_id": row.segment_id,
                "speaker": row.speaker,
                "text": row.text,
                "cleaned_text": row.cleaned_text,
                "sequence_number": row.sequence_number,
                "start_time": float(row.start_time) if row.start_time is not None else None,
                "end_time": float(row.end_time) if row.end_time is not None else None,
            }
            for row in rows
        ]

    def _persist_chunks(self, transcript: Transcript, chunks: list) -> None:
        from app.db.repositories import transcripts as repo

        repo.replace_chunks(self.db, transcript, chunks)
