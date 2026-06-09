import re
from dataclasses import dataclass

from app.core.logging import get_logger

logger = get_logger(__name__)

FILLER_WORDS: frozenset[str] = frozenset(
    {
        "um",
        "uh",
        "umm",
        "uhh",
        "ah",
        "ahh",
        "er",
        "err",
        "hmm",
        "hm",
        "mm",
        "huh",
        "uh-huh",
        "uh huh",
        "mm-hmm",
        "mm hmm",
        "mhm",
        "like",
        "you know",
        "i mean",
        "sort of",
        "kind of",
        "right",
        "so",
        "well",
        "basically",
        "actually",
        "literally",
        "honestly",
    }
)

FILLER_PATTERN = re.compile(
    r"\b(?:um+|uh+|ah+|er+|hmm+|hm+|mm+|huh|uh[\s-]huh|mm[\s-]hmm|mhm+)\b",
    re.IGNORECASE,
)

CONTEXTUAL_FILLER_PATTERN = re.compile(
    r"\b(?:you know|I mean|sort of|kind of|basically|actually|literally|honestly)\b",
    re.IGNORECASE,
)

SENTENCE_START_FILLER_PATTERN = re.compile(
    r"^(?:like|right|so|well)\s+",
    re.IGNORECASE,
)

NONVERBAL_ANNOTATION_PATTERN = re.compile(
    r"(?:\[.*?\]|\(.*?\)|\{.*?\}|<[^>]+>)",
    re.DOTALL,
)

SPECIFIC_NONVERBAL_PATTERN = re.compile(
    r"(?:"
    r"\[laughter\]|\(laughter\)|\[laughs?\]|\(laughs?\)"
    r"|\[cough(?:ing)?\]|\(cough(?:ing)?\)"
    r"|\[sigh(?:s|ing)?\]|\(sigh(?:s|ing)?\)"
    r"|\[clears?\s*throat\]|\(clears?\s*throat\)"
    r"|\[silence\]|\(silence\)"
    r"|\[pause\]|\(pause\)"
    r"|\[music\]|\(music\)"
    r"|\[applause\]|\(applause\)"
    r"|\[indistinct\]|\(indistinct\)"
    r"|\[inaudible\]|\(inaudible\)"
    r"|\[unintelligible\]|\(unintelligible\)"
    r"|\[crosstalk\]|\(crosstalk\)"
    r"|\[background\s*\w*\]|\(background\s*\w*\)"
    r")",
    re.IGNORECASE,
)

FORMATTING_ARTIFACT_PATTERN = re.compile(
    r"(?:"
    r"&amp;|&lt;|&gt;|&nbsp;|&quot;|&apos;"
    r"|\\n|\\r|\\t"
    r"|\u200b|\u200c|\u200d|\ufeff"
    r"|\u00a0"
    r")",
)

EXCESSIVE_WHITESPACE_PATTERN = re.compile(r"\s+")

TRAILING_PUNCTUATION_WHITESPACE_PATTERN = re.compile(r"\s+([.,;:!?)\]}])")

REPEATED_PUNCTUATION_PATTERN = re.compile(r"([.,;:!?])\1{2,}")

DANGLING_HYPHEN_PATTERN = re.compile(r"\s+-\s+")

SENTENCE_START_DANGLING_PATTERN = re.compile(r"^[—–\-]+\s*")


@dataclass(frozen=True)
class CleaningResult:
    cleaned_text: str
    fillers_removed: int
    annotations_removed: int
    artifacts_removed: int
    whitespace_collapsed: int


class TranscriptCleaner:
    def clean(self, text: str) -> CleaningResult:
        if not text or not text.strip():
            return CleaningResult(
                cleaned_text="",
                fillers_removed=0,
                annotations_removed=0,
                artifacts_removed=0,
                whitespace_collapsed=0,
            )

        current = text

        current, annotations_count = self._remove_nonverbal_annotations(current)
        current, artifacts_count = self._remove_formatting_artifacts(current)
        current, fillers_count = self._remove_filler_words(current)
        current, whitespace_count = self._normalize_whitespace(current)
        current = self._fix_punctuation(current)
        current = self._clean_dangling_characters(current)
        current = current.strip()

        if not current:
            logger.info(
                "transcript_cleaner.empty_after_cleaning",
                extra={"original_text_length": len(text)},
            )

        return CleaningResult(
            cleaned_text=current,
            fillers_removed=fillers_count,
            annotations_removed=annotations_count,
            artifacts_removed=artifacts_count,
            whitespace_collapsed=whitespace_count,
        )

    def _remove_nonverbal_annotations(self, text: str) -> tuple[str, int]:
        result = SPECIFIC_NONVERBAL_PATTERN.sub(" ", text)
        result = NONVERBAL_ANNOTATION_PATTERN.sub(
            lambda m: m.group(0) if self._is_content_bracket(m.group(0)) else " ",
            result,
        )
        count = len(SPECIFIC_NONVERBAL_PATTERN.findall(text)) + len(
            NONVERBAL_ANNOTATION_PATTERN.findall(text)
        )
        return result, count

    @staticmethod
    def _is_content_bracket(match: str) -> bool:
        content = match[1:-1].strip()
        if not content:
            return False
        if len(content.split()) > 4:
            return True
        return False

    def _remove_formatting_artifacts(self, text: str) -> tuple[str, int]:
        count = len(FORMATTING_ARTIFACT_PATTERN.findall(text))
        result = FORMATTING_ARTIFACT_PATTERN.sub("", text)
        html_entity_map = {
            "&amp;": "&",
            "&lt;": "<",
            "&gt;": ">",
            "&nbsp;": " ",
            "&quot;": '"',
            "&apos;": "'",
        }
        for entity, replacement in html_entity_map.items():
            if entity in result:
                result = result.replace(entity, replacement)
        return result, count

    def _remove_filler_words(self, text: str) -> tuple[str, int]:
        total_removed = 0

        result, count = self._remove_simple_fillers(text)
        total_removed += count

        result, count = self._remove_contextual_fillers(result)
        total_removed += count

        result, count = self._remove_sentence_start_fillers(result)
        total_removed += count

        return result, total_removed

    @staticmethod
    def _remove_simple_fillers(text: str) -> tuple[str, int]:
        count = len(FILLER_PATTERN.findall(text))
        result = FILLER_PATTERN.sub("", text)
        return result, count

    @staticmethod
    def _remove_contextual_fillers(text: str) -> tuple[str, int]:
        count = len(CONTEXTUAL_FILLER_PATTERN.findall(text))
        result = CONTEXTUAL_FILLER_PATTERN.sub("", text)
        return result, count

    @staticmethod
    def _remove_sentence_start_fillers(text: str) -> tuple[str, int]:
        count = 0
        result = SENTENCE_START_FILLER_PATTERN.sub("", text, count=1)
        if result != text:
            count = 1
        return result, count

    @staticmethod
    def _normalize_whitespace(text: str) -> tuple[str, int]:
        original_len = len(text)
        result = EXCESSIVE_WHITESPACE_PATTERN.sub(" ", text)
        collapsed = original_len - len(result)
        return result, max(collapsed, 0)

    @staticmethod
    def _fix_punctuation(text: str) -> str:
        result = TRAILING_PUNCTUATION_WHITESPACE_PATTERN.sub(r"\1", text)
        result = REPEATED_PUNCTUATION_PATTERN.sub(r"\1\1", result)
        return result

    @staticmethod
    def _clean_dangling_characters(text: str) -> str:
        result = DANGLING_HYPHEN_PATTERN.sub(" ", text)
        result = SENTENCE_START_DANGLING_PATTERN.sub("", result)
        return result
