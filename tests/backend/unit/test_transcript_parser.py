from pathlib import Path

import pytest

from app.services.transcript_parser import (
    VttParser,
    VttParsingError,
    ZoomChatParser,
    ZoomChatParsingError,
    detect_zoom_chat_format,
)


FIXTURES_DIR = Path(__file__).resolve().parents[2] / "fixtures"


class TestZoomChatParser:
    def test_parse_zoom_chat_extracts_segments(self) -> None:
        segments = ZoomChatParser().parse_file(FIXTURES_DIR / "sample_zoom_chat.txt")

        assert len(segments) == 8

        assert segments[0].sequence_number == 1
        assert segments[0].start_time == 5.0
        assert segments[0].end_time == 6.0
        assert segments[0].speaker == "Alice"
        assert segments[0].text == "Hi everyone, welcome to the standup."

        assert segments[1].speaker == "Bob"
        assert segments[1].text == "Thanks Alice, I have a quick update on the backend."
        assert segments[1].start_time == 12.0

        assert segments[3].speaker == "Carol"
        assert segments[3].text == "Great, I'll start QA testing this afternoon."

        assert segments[5].speaker == "David"
        assert segments[5].start_time == 62.0

    def test_parse_zoom_chat_multiline_timestamp(self) -> None:
        content = "00:27:08 User Name: Hello world\n00:27:18 Jane Doe: Second message\n"
        segments = ZoomChatParser().parse(content)

        assert len(segments) == 2
        assert segments[0].start_time == 1628.0
        assert segments[0].speaker == "User Name"
        assert segments[0].text == "Hello world"
        assert segments[1].start_time == 1638.0
        assert segments[1].speaker == "Jane Doe"

    def test_parse_zoom_chat_raises_when_no_valid_lines(self) -> None:
        with pytest.raises(ZoomChatParsingError):
            ZoomChatParser().parse_file(FIXTURES_DIR / "malformed_zoom_chat.txt")

    def test_parse_zoom_chat_raises_on_empty_content(self) -> None:
        with pytest.raises(ZoomChatParsingError):
            ZoomChatParser().parse("")

    def test_parse_zoom_chat_skips_empty_messages(self) -> None:
        content = "00:01:00 Alice:\n00:01:30 Bob: Actual message\n"
        segments = ZoomChatParser().parse(content)

        assert len(segments) == 1
        assert segments[0].speaker == "Bob"
        assert segments[0].text == "Actual message"

    def test_parse_zoom_chat_handles_various_timestamps(self) -> None:
        content = "00:00:00 Alice: Start\n01:30:45 Bob: Deep in meeting\n"
        segments = ZoomChatParser().parse(content)

        assert segments[0].start_time == 0.0
        assert segments[1].start_time == 5445.0


class TestDetectZoomChatFormat:
    def test_detects_zoom_chat_format(self) -> None:
        content = "00:00:05 Alice: Hello\n00:00:10 Bob: Hi there\n"
        assert detect_zoom_chat_format(content) is True

    def test_rejects_vtt_format(self) -> None:
        content = "WEBVTT\n\n00:00:01.000 --> 00:00:04.000\nAlice: Hello\n"
        assert detect_zoom_chat_format(content) is False

    def test_rejects_empty_content(self) -> None:
        assert detect_zoom_chat_format("") is False

    def test_rejects_random_text(self) -> None:
        content = "Just some random lines\nwithout any timestamps\nor chat format\n"
        assert detect_zoom_chat_format(content) is False

    def test_detects_mixed_with_some_non_matching_lines(self) -> None:
        content = "00:00:05 Alice: Hello\nSome metadata line\n00:00:10 Bob: Hi\n"
        assert detect_zoom_chat_format(content) is True


class TestVttParserStillWorks:
    def test_parse_vtt_extracts_segments(self) -> None:
        segments = VttParser().parse_file(FIXTURES_DIR / "sample_transcript.vtt")
        assert len(segments) == 4
        assert segments[0].speaker == "Alice"
        assert segments[0].text == "Welcome to the weekly sync."

    def test_parse_vtt_raises_when_no_valid_cues(self) -> None:
        with pytest.raises(VttParsingError):
            VttParser().parse_file(FIXTURES_DIR / "malformed_transcript.vtt")
