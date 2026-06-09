import base64
import time
from dataclasses import dataclass

import httpx

from app.core.config import Settings, settings
from app.core.errors import ConfigurationError, ExternalServiceError
from app.core.logging import get_logger
from app.integrations.zoom.retry import retry_sync

logger = get_logger(__name__)


@dataclass(frozen=True)
class ZoomAccessToken:
    access_token: str
    token_type: str
    expires_in: int
    expires_at: float
    scope: str | None = None
    api_url: str | None = None


class ZoomOAuthClient:
    """Server-to-Server OAuth client.

    Zoom's account_credentials grant does not issue refresh tokens. Token refresh is handled by
    requesting a new access token when the cached token is near expiry.
    """

    def __init__(self, config: Settings = settings) -> None:
        self.config = config
        self._cached_token: ZoomAccessToken | None = None

    def get_access_token(self, *, force_refresh: bool = False) -> ZoomAccessToken:
        if not force_refresh and self._cached_token and self._cached_token.expires_at > time.time() + 60:
            return self._cached_token

        self._cached_token = self._request_access_token()
        return self._cached_token

    def _request_access_token(self) -> ZoomAccessToken:
        self._validate_config()
        auth_header = self._basic_authorization_header()
        data = {
            "grant_type": "account_credentials",
            "account_id": self.config.zoom_account_id,
        }

        def send_request() -> httpx.Response:
            return httpx.post(
                self.config.zoom_token_url,
                data=data,
                headers={
                    "Authorization": auth_header,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                timeout=self.config.zoom_oauth_timeout_seconds,
            )

        try:
            response = retry_sync(
                send_request,
                attempts=self.config.zoom_oauth_retry_attempts,
                backoff_seconds=self.config.zoom_oauth_retry_backoff_seconds,
                retry_on_status={429, 500, 502, 503, 504},
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.exception("zoom_oauth.token_request_failed")
            raise ExternalServiceError("Failed to generate Zoom access token") from exc

        payload = response.json()
        access_token = payload.get("access_token")
        if not access_token:
            raise ExternalServiceError("Zoom access token response did not include access_token")

        expires_in = int(payload.get("expires_in", 3600))
        token = ZoomAccessToken(
            access_token=access_token,
            token_type=payload.get("token_type", "bearer"),
            expires_in=expires_in,
            expires_at=time.time() + expires_in,
            scope=payload.get("scope"),
            api_url=payload.get("api_url"),
        )
        logger.info(
            "zoom_oauth.token_generated",
            extra={"expires_in": token.expires_in, "scope": token.scope},
        )
        return token

    def _validate_config(self) -> None:
        missing = [
            name
            for name, value in {
                "ZOOM_ACCOUNT_ID": self.config.zoom_account_id,
                "ZOOM_CLIENT_ID": self.config.zoom_client_id,
                "ZOOM_CLIENT_SECRET": self.config.zoom_client_secret,
            }.items()
            if not value
        ]
        if missing:
            raise ConfigurationError(f"Missing required Zoom OAuth settings: {', '.join(missing)}")

    def _basic_authorization_header(self) -> str:
        raw_credentials = f"{self.config.zoom_client_id}:{self.config.zoom_client_secret}".encode()
        encoded = base64.b64encode(raw_credentials).decode("ascii")
        return f"Basic {encoded}"
