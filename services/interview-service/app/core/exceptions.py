"""Centralized application exceptions and their HTTP mappings."""
from __future__ import annotations


class AppError(Exception):
    """Base class for all application-level errors."""

    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, message: str = "An unexpected error occurred", **extra):
        self.message = message
        self.extra = extra
        super().__init__(message)


class NotFoundError(AppError):
    status_code = 404
    error_code = "not_found"

    def __init__(self, message: str = "Resource not found", **extra):
        super().__init__(message, **extra)


class ValidationAppError(AppError):
    status_code = 422
    error_code = "validation_error"

    def __init__(self, message: str = "Invalid request", **extra):
        super().__init__(message, **extra)


class UnauthorizedError(AppError):
    status_code = 401
    error_code = "unauthorized"

    def __init__(self, message: str = "Authentication required", **extra):
        super().__init__(message, **extra)


class ForbiddenError(AppError):
    status_code = 403
    error_code = "forbidden"

    def __init__(self, message: str = "You do not have access to this resource", **extra):
        super().__init__(message, **extra)


class ConflictError(AppError):
    status_code = 409
    error_code = "conflict"

    def __init__(self, message: str = "Resource state conflict", **extra):
        super().__init__(message, **extra)


class InvalidStateTransitionError(ConflictError):
    error_code = "invalid_state_transition"

    def __init__(self, message: str = "Invalid state transition", **extra):
        super().__init__(message, **extra)


class ExternalServiceError(AppError):
    status_code = 502
    error_code = "external_service_error"

    def __init__(self, message: str = "An upstream service failed", **extra):
        super().__init__(message, **extra)


class ServiceUnavailableError(AppError):
    status_code = 503
    error_code = "service_unavailable"

    def __init__(self, message: str = "Service temporarily unavailable", **extra):
        super().__init__(message, **extra)
