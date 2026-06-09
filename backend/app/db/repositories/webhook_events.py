from datetime import UTC, datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.models.webhook_event import WebhookEvent


def get_existing_event(
    db: Session, zoom_event_id: str | None, request_body_sha256: str
) -> WebhookEvent | None:
    conditions = [WebhookEvent.request_body_sha256 == request_body_sha256]
    if zoom_event_id:
        conditions.append(WebhookEvent.zoom_event_id == zoom_event_id)
    return db.scalar(select(WebhookEvent).where(or_(*conditions)).limit(1))


def create_event(
    db: Session,
    *,
    event_type: str,
    zoom_event_id: str | None,
    request_body_sha256: str,
    payload: dict,
    headers: dict,
    status: str = "received",
) -> WebhookEvent:
    event = WebhookEvent(
        event_type=event_type,
        zoom_event_id=zoom_event_id,
        request_body_sha256=request_body_sha256,
        payload=payload,
        headers=headers,
        status=status,
    )
    db.add(event)
    db.flush()
    return event


def mark_processed(db: Session, event: WebhookEvent, *, meeting_id=None, status: str = "processed") -> None:
    event.status = status
    event.meeting_id = meeting_id
    event.processed_at = datetime.now(UTC)
    db.flush()


def mark_failed(db: Session, event: WebhookEvent, error_message: str) -> None:
    event.status = "failed"
    event.error_message = error_message
    event.processed_at = datetime.now(UTC)
    db.flush()
