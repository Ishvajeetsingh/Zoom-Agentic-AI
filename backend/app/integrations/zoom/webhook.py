import hashlib
import hmac
import time
from collections.abc import Mapping

from app.core.config import Settings, settings
from app.core.errors import ConfigurationError


class ZoomWebhookError(ValueError):
    """Raised when a Zoom webhook cannot be verified or handled."""


def verify_zoom_webhook_request(
    *,
    headers: Mapping[str, str],
    raw_body: bytes,
    config: Settings = settings,
) -> None:
    if not config.zoom_webhook_verify_signature:
        return

    if not config.zoom_webhook_secret_token:
        raise ConfigurationError("ZOOM_WEBHOOK_SECRET_TOKEN is required for webhook verification")

    timestamp = headers.get("x-zm-request-timestamp")
    received_signature = headers.get("x-zm-signature")
    if not timestamp or not received_signature:
        raise ZoomWebhookError("Missing Zoom webhook signature headers")

    _validate_timestamp(timestamp, config.zoom_webhook_tolerance_seconds)
    expected_signature = compute_zoom_signature(
        secret_token=config.zoom_webhook_secret_token,
        timestamp=timestamp,
        raw_body=raw_body,
    )
    if not hmac.compare_digest(expected_signature, received_signature):
        raise ZoomWebhookError("Invalid Zoom webhook signature")


def compute_zoom_signature(*, secret_token: str, timestamp: str, raw_body: bytes) -> str:
    message = b"v0:" + timestamp.encode("utf-8") + b":" + raw_body
    digest = hmac.new(secret_token.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return f"v0={digest}"


def build_url_validation_response(payload: dict, config: Settings = settings) -> dict[str, str]:
    if not config.zoom_webhook_secret_token:
        raise ConfigurationError("ZOOM_WEBHOOK_SECRET_TOKEN is required for URL validation")

    plain_token = payload.get("payload", {}).get("plainToken")
    if not plain_token:
        raise ZoomWebhookError("Missing Zoom URL validation plainToken")

    encrypted_token = hmac.new(
        config.zoom_webhook_secret_token.encode("utf-8"),
        plain_token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return {"plainToken": plain_token, "encryptedToken": encrypted_token}


def body_sha256(raw_body: bytes) -> str:
    return hashlib.sha256(raw_body).hexdigest()


def sanitize_headers(headers: Mapping[str, str]) -> dict[str, str]:
    allowed_prefixes = ("x-zm-", "content-", "user-agent")
    sanitized: dict[str, str] = {}
    for key, value in headers.items():
        lower_key = key.lower()
        if lower_key == "authorization":
            sanitized[key] = "[redacted]"
        elif lower_key.startswith(allowed_prefixes):
            sanitized[key] = value
    return sanitized


def _validate_timestamp(timestamp: str, tolerance_seconds: int) -> None:
    try:
        request_time = int(timestamp)
    except ValueError as exc:
        raise ZoomWebhookError("Invalid Zoom webhook timestamp") from exc

    if abs(int(time.time()) - request_time) > tolerance_seconds:
        raise ZoomWebhookError("Zoom webhook timestamp is outside the allowed tolerance")
