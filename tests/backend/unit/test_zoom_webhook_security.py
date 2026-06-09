import json

from app.integrations.zoom.webhook import (
    build_url_validation_response,
    compute_zoom_signature,
    verify_zoom_webhook_request,
)


class Config:
    zoom_webhook_verify_signature = True
    zoom_webhook_secret_token = "test-secret"
    zoom_webhook_tolerance_seconds = 999999999


def test_compute_zoom_signature_matches_verifier() -> None:
    body = json.dumps({"event": "recording.completed"}).encode("utf-8")
    timestamp = "1739923528"
    signature = compute_zoom_signature(
        secret_token=Config.zoom_webhook_secret_token,
        timestamp=timestamp,
        raw_body=body,
    )

    verify_zoom_webhook_request(
        headers={"x-zm-request-timestamp": timestamp, "x-zm-signature": signature},
        raw_body=body,
        config=Config,
    )


def test_build_url_validation_response() -> None:
    response = build_url_validation_response(
        {"event": "endpoint.url_validation", "payload": {"plainToken": "abc123"}},
        config=Config,
    )

    assert response["plainToken"] == "abc123"
    assert len(response["encryptedToken"]) == 64
