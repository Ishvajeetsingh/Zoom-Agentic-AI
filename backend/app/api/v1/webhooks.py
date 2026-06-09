import json

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.errors import ConfigurationError
from app.core.logging import get_logger
from app.integrations.zoom.webhook import (
    ZoomWebhookError,
    build_url_validation_response,
    verify_zoom_webhook_request,
)
from app.services.zoom_webhook_service import ZoomWebhookService

router = APIRouter()
logger = get_logger(__name__)


@router.post("/zoom", status_code=status.HTTP_200_OK)
async def receive_zoom_webhook(request: Request, db: Session = Depends(get_db)) -> dict[str, object]:
    raw_body = await request.body()

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        logger.warning("zoom_webhook.invalid_json", extra={"error": str(exc)})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload") from exc

    try:
        verify_zoom_webhook_request(headers=request.headers, raw_body=raw_body)
    except ZoomWebhookError as exc:
        logger.warning("zoom_webhook.security_rejected", extra={"reason": str(exc)})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except ConfigurationError as exc:
        logger.error("zoom_webhook.configuration_error", extra={"reason": str(exc)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Zoom webhook verification is not configured",
        ) from exc

    if payload.get("event") == "endpoint.url_validation":
        logger.info("zoom_webhook.url_validation")
        try:
            return build_url_validation_response(payload)
        except (ZoomWebhookError, ConfigurationError) as exc:
            logger.warning("zoom_webhook.url_validation_failed", extra={"reason": str(exc)})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    service = ZoomWebhookService(db)
    try:
        result = service.handle_event(payload=payload, headers=dict(request.headers), raw_body=raw_body)
        db.commit()
        return result
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("zoom_webhook.database_error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store Zoom webhook metadata",
        ) from exc
    except ZoomWebhookError as exc:
        db.rollback()
        logger.warning("zoom_webhook.processing_error", extra={"reason": str(exc)})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
