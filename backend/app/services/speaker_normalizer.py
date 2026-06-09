import re
from dataclasses import dataclass, field

from app.core.logging import get_logger

logger = get_logger(__name__)

SPEAKER_LABEL_PATTERN = re.compile(r"^Speaker[_\s](\d+)$", re.IGNORECASE)

GENERIC_SPEAKER_PATTERN = re.compile(
    r"^(?:unknown|unidentified|anonymous|n/a|none|null|speaker\s*\d*)$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class SpeakerNormalizationResult:
    speaker_map: dict[str | None, str]
    speakers_normalized: int
    null_speakers_assigned: int


class SpeakerNormalizer:
    def build_meeting_speaker_map(
        self, segments: list[dict], meeting_id: str | None = None
    ) -> dict[str | None, str]:
        known_speakers: dict[str, str] = {}
        null_counter = 0
        speaker_map: dict[str | None, str] = {}

        for segment in segments:
            raw_speaker = segment.get("speaker")
            if raw_speaker is None:
                key = None
            else:
                stripped = raw_speaker.strip()
                if not stripped:
                    key = None
                else:
                    key = stripped

            if key in speaker_map:
                continue

            if key is None or self._is_generic_label(key):
                null_counter += 1
                fallback = f"Speaker_{null_counter}"
                speaker_map[key] = fallback
                logger.info(
                    "speaker_normalizer.fallback_assigned",
                    extra={
                        "meeting_id": str(meeting_id) if meeting_id else None,
                        "raw_speaker": repr(key),
                        "fallback_label": fallback,
                    },
                )
            else:
                normalized = self._normalize_known_speaker(key)
                if normalized not in known_speakers.values():
                    known_speakers[key] = normalized
                    speaker_map[key] = normalized
                else:
                    existing_key = self._find_key_by_value(known_speakers, normalized)
                    if existing_key is not None and existing_key in speaker_map:
                        speaker_map[key] = speaker_map[existing_key]
                    else:
                        known_speakers[key] = normalized
                        speaker_map[key] = normalized

        return speaker_map

    def normalize_segments(
        self, segments: list[dict], speaker_map: dict[str | None, str]
    ) -> SpeakerNormalizationResult:
        null_speakers_assigned = 0
        speakers_normalized = 0

        for segment in segments:
            raw_speaker = segment.get("speaker")
            key = self._resolve_key(raw_speaker)

            if key not in speaker_map:
                continue

            new_label = speaker_map[key]
            current_label = segment.get("speaker")

            if current_label != new_label:
                if key is None or self._is_generic_label(key) if key else True:
                    null_speakers_assigned += 1
                else:
                    speakers_normalized += 1
                segment["speaker"] = new_label

        return SpeakerNormalizationResult(
            speaker_map=speaker_map,
            speakers_normalized=speakers_normalized,
            null_speakers_assigned=null_speakers_assigned,
        )

    @staticmethod
    def _resolve_key(raw_speaker: str | None) -> str | None:
        if raw_speaker is None:
            return None
        stripped = raw_speaker.strip()
        if not stripped:
            return None
        return stripped

    @staticmethod
    def _is_generic_label(label: str) -> bool:
        if SPEAKER_LABEL_PATTERN.match(label):
            return True
        if GENERIC_SPEAKER_PATTERN.match(label):
            return True
        return False

    @staticmethod
    def _normalize_known_speaker(name: str) -> str:
        normalized = name.strip()
        normalized = re.sub(r"\s+", " ", normalized)
        if len(normalized) > 1:
            normalized = normalized[0].upper() + normalized[1:]
        return normalized

    @staticmethod
    def _find_key_by_value(mapping: dict, value: str) -> str | None:
        for k, v in mapping.items():
            if v == value:
                return k
        return None
