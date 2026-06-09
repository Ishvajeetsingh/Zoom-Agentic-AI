from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.repositories import meetings, transcripts, webhook_events
from app.integrations.zoom.webhook import ZoomWebhookError, body_sha256, sanitize_headers

logger = get_logger(__name__)


class ZoomWebhookService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def handle_event(self, *, payload: dict[str, Any], headers: dict[str, str], raw_body: bytes) -> dict[str, Any]:
        event_type = payload.get("event")
        if not event_type:
            raise ZoomWebhookError("Zoom webhook payload is missing event")

        request_hash = body_sha256(raw_body)
        zoom_event_id = self._event_identifier(headers, payload)
        existing_event = webhook_events.get_existing_event(self.db, zoom_event_id, request_hash)
        if existing_event:
            logger.info(
                "zoom_webhook.duplicate_ignored",
                extra={"event_type": event_type, "event_id": str(existing_event.id)},
            )
            return {"status": "duplicate", "event_id": str(existing_event.id)}

        event = webhook_events.create_event(
            self.db,
            event_type=event_type,
            zoom_event_id=zoom_event_id,
            request_body_sha256=request_hash,
            payload=payload,
            headers=sanitize_headers(headers),
        )

        if event_type != "recording.completed":
            webhook_events.mark_processed(self.db, event, status="ignored")
            logger.info("zoom_webhook.ignored_event", extra={"event_type": event_type})
            return {"status": "ignored", "event": event_type, "event_id": str(event.id)}

        try:
            meeting, transcript_count = self._handle_recording_completed(payload)
            webhook_events.mark_processed(self.db, event, meeting_id=meeting.id)
        except Exception as exc:
            webhook_events.mark_failed(self.db, event, str(exc))
            raise

        logger.info(
            "zoom_webhook.recording_completed_processed",
            extra={
                "event_id": str(event.id),
                "meeting_id": str(meeting.id),
                "transcript_count": transcript_count,
            },
        )
        return {
            "status": "processed",
            "event": event_type,
            "event_id": str(event.id),
            "meeting_id": str(meeting.id),
            "transcript_metadata_records": transcript_count,
        }

    def _handle_recording_completed(self, payload: dict[str, Any]):
        event_payload = payload.get("payload") or {}
        meeting_object = event_payload.get("object") or {}
        if not meeting_object:
            raise ZoomWebhookError("recording.completed payload is missing object")

        meeting = meetings.upsert_zoom_meeting(
            self.db,
            {
                "source": "zoom",
                "zoom_meeting_id": _to_optional_str(meeting_object.get("id")),
                "zoom_uuid": _to_optional_str(meeting_object.get("uuid")),
                "account_id": _to_optional_str(event_payload.get("account_id")),
                "host_id": _to_optional_str(meeting_object.get("host_id")),
                "host_email": _to_optional_str(meeting_object.get("host_email")),
                "topic": meeting_object.get("topic"),
                "start_time": _parse_datetime(meeting_object.get("start_time")),
                "timezone": meeting_object.get("timezone"),
                "duration_minutes": _to_optional_int(meeting_object.get("duration")),
                "participant_count": _to_optional_int(meeting_object.get("participant_count")),
                "metadata_json": meeting_object,
            },
        )

        transcript_files = [
            file
            for file in meeting_object.get("recording_files", []) or []
            if _looks_like_transcript(file)
        ]
        for file in transcript_files:
            transcripts.upsert_transcript_metadata(
                self.db,
                {
                    "meeting_id": meeting.id,
                    "source_format": _source_format(file),
                    "status": "metadata_received",
                    "zoom_file_id": _to_optional_str(file.get("id")),
                    "zoom_recording_type": file.get("recording_type"),
                    "file_type": file.get("file_type"),
                    "file_extension": file.get("file_extension"),
                    "file_size_bytes": _to_optional_int(file.get("file_size")),
                    "recording_start": _parse_datetime(file.get("recording_start")),
                    "recording_end": _parse_datetime(file.get("recording_end")),
                    "play_url": file.get("play_url"),
                    "download_url": file.get("download_url"),
                    "language": file.get("language"),
                    "metadata_json": file,
                },
            )

        return meeting, len(transcript_files)

    @staticmethod
    def _event_identifier(headers: dict[str, str], payload: dict[str, Any]) -> str | None:
        for key in ("x-zm-request-id", "x-zm-trackingid", "x-zm-tracking-id"):
            if headers.get(key):
                return headers[key]
        event_ts = payload.get("event_ts")
        event = payload.get("event")
        meeting_uuid = ((payload.get("payload") or {}).get("object") or {}).get("uuid")
        if event and event_ts and meeting_uuid:
            return f"{event}:{meeting_uuid}:{event_ts}"
        return None


def _looks_like_transcript(file: dict[str, Any]) -> bool:
    file_type = str(file.get("file_type") or "").upper()
    extension = str(file.get("file_extension") or "").upper()
    recording_type = str(file.get("recording_type") or "").lower()
    return file_type in {"TRANSCRIPT", "CC", "VTT"} or extension in {"VTT", "JSON"} or "transcript" in recording_type


def _source_format(file: dict[str, Any]) -> str | None:
    extension = str(file.get("file_extension") or "").lower()
    if extension:
        return extension
    file_type = str(file.get("file_type") or "").lower()
    return file_type or None


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def _to_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _to_optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
