import re
from dataclasses import dataclass, field

from app.core.logging import get_logger

logger = get_logger(__name__)

DEFAULT_TARGET_WORDS = 300
MIN_CHUNK_WORDS = 50
MAX_CHUNK_WORDS = 500

SENTENCE_END_PATTERN = re.compile(r"[.!?]\s*$")
TOPIC_SHIFT_PATTERNS = [
    re.compile(r"^(?:now|next|moving\s+on|let'?s\s+(?:move|talk|discuss|look|switch|turn|go))\b", re.IGNORECASE),
    re.compile(r"^(?:so\s*,?\s*(?:let'?s|we|I|the|that|this|what|how|why|when|where|are|is|do|can|will|should))\b", re.IGNORECASE),
    re.compile(r"^(?:anyway|alright|okay|ok\s*,|well\s*,)\b", re.IGNORECASE),
]
PAUSE_THRESHOLD_SECONDS = 15.0


@dataclass(frozen=True)
class ChunkData:
    text: str
    word_count: int
    speakers: list[str]
    segment_ids: list[str]
    segment_range_start: int
    segment_range_end: int
    start_time: float | None
    end_time: float | None


@dataclass
class ChunkingResult:
    chunks: list[ChunkData] = field(default_factory=list)
    total_chunks: int = 0
    total_words: int = 0
    segments_merged: int = 0


class SemanticChunker:
    def __init__(
        self,
        target_words: int = DEFAULT_TARGET_WORDS,
        min_words: int = MIN_CHUNK_WORDS,
        max_words: int = MAX_CHUNK_WORDS,
        pause_threshold: float = PAUSE_THRESHOLD_SECONDS,
    ) -> None:
        self.target_words = target_words
        self.min_words = min_words
        self.max_words = max_words
        self.pause_threshold = pause_threshold

    def chunk(self, segments: list[dict]) -> ChunkingResult:
        if not segments:
            logger.info("semantic_chunker.no_segments")
            return ChunkingResult()

        boundaries = self._find_boundaries(segments)
        chunks = self._build_chunks(segments, boundaries)

        total_words = sum(c.word_count for c in chunks)
        result = ChunkingResult(
            chunks=chunks,
            total_chunks=len(chunks),
            total_words=total_words,
            segments_merged=len(segments),
        )

        logger.info(
            "semantic_chunker.completed",
            extra={
                "total_chunks": result.total_chunks,
                "total_words": result.total_words,
                "segments_merged": result.segments_merged,
            },
        )

        return result

    def _find_boundaries(self, segments: list[dict]) -> list[int]:
        boundaries: list[int] = []
        running_words = 0

        for i in range(1, len(segments)):
            prev = segments[i - 1]
            curr = segments[i]

            running_words += len(prev.get("cleaned_text", "").split())

            if self._is_boundary(prev, curr, running_words):
                boundaries.append(i)
                running_words = 0

        return boundaries

    def _is_boundary(self, prev: dict, curr: dict, running_words: int) -> bool:
        if running_words >= self.max_words:
            return True

        pause = self._compute_pause(prev, curr)
        if pause >= self.pause_threshold and running_words >= self.min_words:
            return True

        curr_text = curr.get("cleaned_text", "")
        if self._is_topic_shift(curr_text) and running_words >= self.min_words:
            return True

        prev_speaker = prev.get("speaker")
        curr_speaker = curr.get("speaker")
        if prev_speaker != curr_speaker and running_words >= self.target_words:
            return True

        if running_words >= self.target_words and self._is_sentence_end(prev.get("cleaned_text", "")):
            return True

        return False

    @staticmethod
    def _compute_pause(prev: dict, curr: dict) -> float:
        prev_end = prev.get("end_time")
        curr_start = curr.get("start_time")
        if prev_end is None or curr_start is None:
            return 0.0
        try:
            return float(curr_start) - float(prev_end)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _is_topic_shift(text: str) -> bool:
        first_sentence = text.strip().split(".")[0] if text.strip() else ""
        return any(p.search(first_sentence) for p in TOPIC_SHIFT_PATTERNS)

    @staticmethod
    def _is_sentence_end(text: str) -> bool:
        return bool(SENTENCE_END_PATTERN.search(text.strip()))

    def _build_chunks(self, segments: list[dict], boundaries: list[int]) -> list[ChunkData]:
        chunks: list[ChunkData] = []
        boundary_set = set(boundaries)
        chunk_index = 0

        current_texts: list[str] = []
        current_speakers: list[str] = []
        current_segment_ids: list[str] = []
        current_seq_start: int | None = None
        current_seq_end: int | None = None
        current_start_time: float | None = None
        current_end_time: float | None = None

        for i, seg in enumerate(segments):
            text = seg.get("cleaned_text") or seg.get("text", "")
            if not text.strip():
                continue

            if current_seq_start is None:
                current_seq_start = seg.get("sequence_number", i)
            current_seq_end = seg.get("sequence_number", i)

            if current_start_time is None and seg.get("start_time") is not None:
                current_start_time = float(seg["start_time"])
            if seg.get("end_time") is not None:
                current_end_time = float(seg["end_time"])

            current_texts.append(text)
            speaker = seg.get("speaker")
            if speaker and speaker not in current_speakers:
                current_speakers.append(speaker)
            seg_id = seg.get("segment_id")
            if seg_id:
                current_segment_ids.append(str(seg_id))

            if i + 1 in boundary_set or i == len(segments) - 1:
                combined_text = " ".join(current_texts)
                word_count = len(combined_text.split())

                chunks.append(
                    ChunkData(
                        text=combined_text,
                        word_count=word_count,
                        speakers=list(current_speakers),
                        segment_ids=list(current_segment_ids),
                        segment_range_start=current_seq_start if current_seq_start is not None else 0,
                        segment_range_end=current_seq_end if current_seq_end is not None else 0,
                        start_time=current_start_time,
                        end_time=current_end_time,
                    )
                )
                chunk_index += 1

                current_texts = []
                current_speakers = []
                current_segment_ids = []
                current_seq_start = None
                current_seq_end = None
                current_start_time = None
                current_end_time = None

        if len(segments) > 0 and not chunks:
            logger.warning(
                "semantic_chunker.no_chunks_produced",
                extra={"segment_count": len(segments)},
            )

        return chunks
