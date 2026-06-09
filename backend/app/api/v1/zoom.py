from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.errors import ConfigurationError, ExternalServiceError
from app.core.logging import get_logger
from app.services.ingestion_service import ZoomIngestionError, ZoomIngestionService

router = APIRouter()
logger = get_logger(__name__)


class ZoomIngestRequest(BaseModel):
    meeting_uuid: str = Field(..., min_length=1, description="Zoom meeting UUID")


class ZoomIngestResponse(BaseModel):
    meeting_id: str
    transcript_id: str | None
    recording_found: bool
    zoom_meeting_id: str | None
    zoom_uuid: str
    topic: str | None


@router.post("/ingest", response_model=ZoomIngestResponse, status_code=status.HTTP_201_CREATED)
def ingest_zoom_meeting(
    request: ZoomIngestRequest,
    db: Session = Depends(get_db),
) -> ZoomIngestResponse:
    service = ZoomIngestionService(db)
    try:
        result = service.ingest_meeting(request.meeting_uuid)
    except ZoomIngestionError as exc:
        db.rollback()
        logger.warning(
            "zoom_ingest.api_error",
            extra={"meeting_uuid": request.meeting_uuid, "error": str(exc)},
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ConfigurationError as exc:
        db.rollback()
        logger.error(
            "zoom_ingest.config_error",
            extra={"meeting_uuid": request.meeting_uuid, "error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Zoom configuration error: {exc}",
        ) from exc
    except ExternalServiceError as exc:
        db.rollback()
        logger.warning(
            "zoom_ingest.external_error",
            extra={"meeting_uuid": request.meeting_uuid, "error": str(exc)},
        )
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("zoom_ingest.database_error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist Zoom ingestion data",
        ) from exc

    return ZoomIngestResponse(
        meeting_id=str(result.meeting_id),
        transcript_id=str(result.transcript_id) if result.transcript_id else None,
        recording_found=result.recording_found,
        zoom_meeting_id=result.zoom_meeting_id,
        zoom_uuid=result.zoom_uuid,
        topic=result.topic,
    )
