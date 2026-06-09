from typing import Any, TypedDict


class ZoomWebhookPayload(TypedDict, total=False):
    event: str
    event_ts: int
    payload: dict[str, Any]
