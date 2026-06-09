import uuid
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.logging import get_logger
from app.db.repositories import transcripts
from app.services.transcript_parser import (
    ParsedTranscriptSegment,
    VttParser,
    VttParsingError,
    ZoomChatParser,
    ZoomChatParsingError,
    detect_zoom_chat_format,
)

logger = get_logger(__name__)


class TranscriptParseError(AppError):
    """Raised when a downloaded transcript cannot be parsed."""


@dataclass(frozen=True)
class TranscriptParseResult:
    transcript_id: uuid.UUID
    meeting_id: uuid.UUID
    status: str
    segment_count: int
    word_count: int


class TranscriptParseService:
    def __init__(
        self,
        db: Session,
        vtt_parser: VttParser | None = None,
        chat_parser: ZoomChatParser | None = None,
    ) -> None:
        self.db = db
        self.vtt_parser = vtt_parser or VttParser()
        self.chat_parser = chat_parser or ZoomChatParser()

    def _select_parser(self, raw_path: Path):
        content = raw_path.read_text(encoding="utf-8-sig", errors="replace")
        if detect_zoom_chat_format(content):
            return self.chat_parser
        return self.vtt_parser

    def parse_transcript(self, transcript_id: uuid.UUID) -> TranscriptParseResult:
        transcript = transcripts.get_by_id(self.db, transcript_id)
        if transcript is None:
            raise TranscriptParseError(f"Transcript not found: {transcript_id}")
        if transcript.status not in {"downloaded", "parsed", "parsing_failed"}:
            raise TranscriptParseError(
                f"Transcript must be downloaded before parsing; current status is {transcript.status}"
            )
        if not transcript.raw_file_path:
            raise TranscriptParseError("Transcript has no local raw file path")

        raw_path = Path(transcript.raw_file_path)
        transcripts.mark_parsing_started(self.db, transcript)
        self.db.commit()

        logger.info(
            "transcript_parse.started",
            extra={"transcript_id": str(transcript.id), "meeting_id": str(transcript.meeting_id)},
        )

        try:
            parser = self._select_parser(raw_path)
            parsed_segments = parser.parse_file(raw_path)
            segment_dicts = [segment.as_dict() for segment in parsed_segments]
            segment_count = transcripts.replace_segments(self.db, transcript, segment_dicts)
            word_count = _count_words(parsed_segments)
            transcripts.mark_parsed(self.db, transcript, segment_count=segment_count, word_count=word_count)
            self.db.commit()
        except (OSError, VttParsingError, ZoomChatParsingError, ValueError) as exc:
            self.db.rollback()
            transcript = transcripts.get_by_id(self.db, transcript_id)
            if transcript is not None:
                transcripts.mark_parsing_failed(self.db, transcript, str(exc))
                self.db.commit()
            logger.exception(
                "transcript_parse.failed",
                extra={"transcript_id": str(transcript_id), "error": str(exc)},
            )
            raise TranscriptParseError(str(exc)) from exc

        logger.info(
            "transcript_parse.completed",
            extra={
                "transcript_id": str(transcript.id),
                "meeting_id": str(transcript.meeting_id),
                "segment_count": segment_count,
                "word_count": word_count,
            },
        )
        return TranscriptParseResult(
            transcript_id=transcript.id,
            meeting_id=transcript.meeting_id,
            status=transcript.status,
            segment_count=segment_count,
            word_count=word_count,
        )


def _count_words(segments: list[ParsedTranscriptSegment]) -> int:
    return sum(len(segment.text.split()) for segment in segments)
