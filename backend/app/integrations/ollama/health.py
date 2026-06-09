"""Ollama health check for readiness endpoint."""

from dataclasses import dataclass, field

from app.core.config import settings
from app.core.logging import get_logger
from app.integrations.ollama.client import OllamaApiClient

logger = get_logger(__name__)


@dataclass
class OllamaReadiness:
    ollama_available: bool = False
    primary_model: str = ""
    primary_model_loaded: bool = False
    fallback_model: str = ""
    fallback_model_loaded: bool = False
    available_models: list[str] = field(default_factory=list)
    latency_seconds: float | None = None
    error: str | None = None


def check_ollama_readiness(
    client: OllamaApiClient | None = None,
) -> OllamaReadiness:
    ollama_client = client or OllamaApiClient()
    result = OllamaReadiness(
        primary_model=settings.ollama_primary_model,
        fallback_model=settings.ollama_fallback_model,
    )

    try:
        status = ollama_client.is_available()
        result.ollama_available = status.available
        result.primary_model_loaded = status.primary_model_loaded
        result.fallback_model_loaded = status.fallback_model_loaded
        result.available_models = status.models
        result.latency_seconds = status.response_latency_seconds
        result.error = status.error
    except Exception as exc:
        result.error = str(exc)
        logger.warning(
            "ollama.readiness_check_failed",
            extra={"error": str(exc)},
        )

    return result
