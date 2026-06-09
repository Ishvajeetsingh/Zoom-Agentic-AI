from pathlib import Path

import pytest

from app.services.transcript_parser import VttParser, VttParsingError


FIXTURES_DIR = Path(__file__).resolve().parents[2] / "fixtures"


def test_parse_vtt_extracts_segments_speakers_and_timestamps() -> None:
    segments = VttParser().parse_file(FIXTURES_DIR / "sample_transcript.vtt")

    assert len(segments) == 4
    assert segments[0].sequence_number == 1
    assert segments[0].start_time == 1.0
    assert segments[0].end_time == 4.0
    assert segments[0].speaker == "Alice"
    assert segments[0].text == "Welcome to the weekly sync."

    assert segments[1].speaker == "Bob"
    assert segments[1].text == "We completed the API integration yesterday."

    assert segments[2].speaker is None
    assert segments[2].text == "The release candidate is ready for testing."

    assert segments[3].sequence_number == 4
    assert segments[3].speaker == "Carol"


def test_parse_vtt_raises_when_no_valid_cues_exist() -> None:
    with pytest.raises(VttParsingError):
        VttParser().parse_file(FIXTURES_DIR / "malformed_transcript.vtt")
