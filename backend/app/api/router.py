from fastapi import APIRouter

from app.api.v1 import (
    exports,
    health,
    meetings,
    metrics,
    processing_runs,
    questions,
    transcripts,
    webhooks,
    zoom,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(zoom.router, prefix="/zoom", tags=["zoom"])
api_router.include_router(meetings.router, prefix="/meetings", tags=["meetings"])
api_router.include_router(transcripts.router, prefix="/transcripts", tags=["transcripts"])
api_router.include_router(processing_runs.router, prefix="/processing-runs", tags=["processing-runs"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(exports.router, prefix="/exports", tags=["exports"])

