import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.logging import get_logger
from app.db.models.transcript import Transcript
from app.db.models.transcript_segment import TranscriptSegment
from app.db.repositories import transcripts as transcript_repo
from app.services.speaker_normalizer import SpeakerNormalizer
from app.services.transcript_cleaner import TranscriptCleaner

logger = get_logger(__name__)


class TranscriptCleaningError(AppError):
    """Raised when transcript cleaning cannot be completed."""


@dataclass(frozen=True)
class TranscriptCleaningResult:
    transcript_id: uuid.UUID
    meeting_id: uuid.UUID
    status: str
    segments_cleaned: int
    speakers_normalized: int
    null_speakers_assigned: int
    total_fillers_removed: int
    total_annotations_removed: int
    total_artifacts_removed: int


class TranscriptCleaningService:
    def __init__(
        self,
        db: Session,
        cleaner: TranscriptCleaner | None = None,
        speaker_normalizer: SpeakerNormalizer | None = None,
    ) -> None:
        self.db = db
        self.cleaner = cleaner or TranscriptCleaner()
        self.speaker_normalizer = speaker_normalizer or SpeakerNormalizer()

    def clean_transcript(self, transcript_id: uuid.UUID) -> TranscriptCleaningResult:
        transcript = transcript_repo.get_by_id(self.db, transcript_id)
        if transcript is None:
            raise TranscriptCleaningError(f"Transcript not found: {transcript_id}")

        if transcript.status not in {"parsed", "cleaning_failed"}:
            raise TranscriptCleaningError(
                f"Transcript must be parsed before cleaning; current status is {transcript.status}"
            )

        transcript_repo.mark_cleaning_started(self.db, transcript)
        self.db.commit()

        logger.info(
            "transcript_cleaning.started",
            extra={
                "transcript_id": str(transcript.id),
                "meeting_id": str(transcript.meeting_id),
            },
        )

        try:
            segments = self._load_segments(transcript)
            if not segments:
                raise TranscriptCleaningError(
                    f"No segments found for transcript {transcript_id}"
                )

            speaker_map = self.speaker_normalizer.build_meeting_speaker_map(
                segments, meeting_id=str(transcript.meeting_id)
            )

            total_fillers = 0
            total_annotations = 0
            total_artifacts = 0
            total_whitespace = 0

            for segment in segments:
                cleaning = self.cleaner.clean(segment["text"])
                segment["cleaned_text"] = cleaning.cleaned_text
                segment["fillers_removed"] = cleaning.fillers_removed
                segment["annotations_removed"] = cleaning.annotations_removed
                segment["artifacts_removed"] = cleaning.artifacts_removed
                total_fillers += cleaning.fillers_removed
                total_annotations += cleaning.annotations_removed
                total_artifacts += cleaning.artifacts_removed
                total_whitespace += cleaning.whitespace_collapsed

            norm_result = self.speaker_normalizer.normalize_segments(
                segments, speaker_map
            )

            self._persist_cleaned_segments(transcript, segments, norm_result)

            cleaned_word_count = sum(
                len(s.get("cleaned_text", "").split()) for s in segments if s.get("cleaned_text")
            )

            transcript_repo.mark_cleaned(
                self.db,
                transcript,
                segments_cleaned=len(segments),
                cleaned_word_count=cleaned_word_count,
            )
            self.db.commit()

        except TranscriptCleaningError:
            self.db.rollback()
            transcript = transcript_repo.get_by_id(self.db, transcript_id)
            if transcript is not None:
                transcript_repo.mark_cleaning_failed(
                    self.db, transcript, "No segments found for transcript"
                )
                self.db.commit()
            raise

        except Exception as exc:
            self.db.rollback()
            transcript = transcript_repo.get_by_id(self.db, transcript_id)
            if transcript is not None:
                transcript_repo.mark_cleaning_failed(self.db, transcript, str(exc))
                self.db.commit()
            logger.exception(
                "transcript_cleaning.failed",
                extra={
                    "transcript_id": str(transcript_id),
                    "error": str(exc),
                },
            )
            raise TranscriptCleaningError(str(exc)) from exc

        logger.info(
            "transcript_cleaning.completed",
            extra={
                "transcript_id": str(transcript.id),
                "meeting_id": str(transcript.meeting_id),
                "segments_cleaned": len(segments),
                "speakers_normalized": norm_result.speakers_normalized,
                "null_speakers_assigned": norm_result.null_speakers_assigned,
                "fillers_removed": total_fillers,
                "annotations_removed": total_annotations,
                "artifacts_removed": total_artifacts,
            },
        )

        return TranscriptCleaningResult(
            transcript_id=transcript.id,
            meeting_id=transcript.meeting_id,
            status=transcript.status,
            segments_cleaned=len(segments),
            speakers_normalized=norm_result.speakers_normalized,
            null_speakers_assigned=norm_result.null_speakers_assigned,
            total_fillers_removed=total_fillers,
            total_annotations_removed=total_annotations,
            total_artifacts_removed=total_artifacts,
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
                "sequence_number": row.sequence_number,
            }
            for row in rows
        ]

    def _persist_cleaned_segments(
        self, transcript: Transcript, segments: list[dict], norm_result
    ) -> None:
        for segment_data in segments:
            row = self.db.get(TranscriptSegment, segment_data["segment_id"])
            if row is None:
                continue
            row.cleaned_text = segment_data.get("cleaned_text")
            row.speaker = segment_data.get("speaker", row.speaker)

        self.db.flush()

        logger.info(
            "transcript_cleaning.segments_persisted",
            extra={
                "transcript_id": str(transcript.id),
                "segment_count": len(segments),
                "speakers_normalized": norm_result.speakers_normalized,
                "null_speakers_assigned": norm_result.null_speakers_assigned,
            },
        )
