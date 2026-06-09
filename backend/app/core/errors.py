class AppError(Exception):
    """Base application exception."""


class NotImplementedModuleError(AppError):
    """Raised when a scaffolded module has not been implemented yet."""


class ConfigurationError(AppError):
    """Raised when required configuration is missing or invalid."""


class ExternalServiceError(AppError):
    """Raised when an external service call fails."""
