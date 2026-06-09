from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.integrations.ollama.health import check_ollama_readiness

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@router.get("/ready")
def readiness_check() -> JSONResponse:
    checks: dict[str, object] = {"status": "ready"}

    ollama = check_ollama_readiness()
    checks["ollama"] = {
        "available": ollama.ollama_available,
        "primary_model": ollama.primary_model,
        "primary_model_loaded": ollama.primary_model_loaded,
        "fallback_model": ollama.fallback_model,
        "fallback_model_loaded": ollama.fallback_model_loaded,
        "available_models": ollama.available_models,
        "latency_seconds": ollama.latency_seconds,
    }
    if ollama.error:
        checks["ollama"]["error"] = ollama.error

    if not ollama.ollama_available:
        checks["status"] = "degraded"

    status_code = 200 if checks["status"] == "ready" else 503
    return JSONResponse(content=checks, status_code=status_code)


@router.get("/ollama")
def ollama_status() -> dict[str, object]:
    ollama = check_ollama_readiness()
    result: dict[str, object] = {
        "available": ollama.ollama_available,
        "primary_model": ollama.primary_model,
        "primary_model_loaded": ollama.primary_model_loaded,
        "fallback_model": ollama.fallback_model,
        "fallback_model_loaded": ollama.fallback_model_loaded,
        "available_models": ollama.available_models,
        "latency_seconds": ollama.latency_seconds,
    }
    if ollama.error:
        result["error"] = ollama.error
    return result
