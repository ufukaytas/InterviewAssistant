"""System endpoints: liveness, readiness, and the dev-only token issuer."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.api.dependencies.settings import get_app_settings
from app.application.schemas.auth_schemas import DevTokenRequest, DevTokenResponse
from app.core.config import Settings
from app.core.exceptions import ForbiddenError, ServiceUnavailableError
from app.core.security import create_dev_access_token

router = APIRouter(tags=["system"])


@router.get("/health", summary="Liveness probe")
async def health() -> dict:
    """Always returns 200 while the process is alive; performs no I/O."""
    return {"status": "ok"}


@router.get("/ready", summary="Readiness probe")
async def ready(request: Request) -> dict:
    """Verifies the application can communicate with MongoDB."""
    mongodb = getattr(request.app.state, "mongodb", None)
    if mongodb is None or not await mongodb.ping():
        raise ServiceUnavailableError("MongoDB is not reachable")
    return {"status": "ready", "mongodb": "connected"}


@router.post(
    "/dev/token",
    response_model=DevTokenResponse,
    summary="Issue a local development JWT (disabled in production)",
)
async def issue_dev_token(
    payload: DevTokenRequest, settings: Settings = Depends(get_app_settings)
) -> DevTokenResponse:
    if not settings.ENABLE_DEV_TOKEN_ENDPOINT or settings.is_production:
        raise ForbiddenError("The development token endpoint is disabled in this environment")

    token = create_dev_access_token(settings, subject=payload.user_id)
    return DevTokenResponse(
        access_token=token,
        expires_in_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    )
