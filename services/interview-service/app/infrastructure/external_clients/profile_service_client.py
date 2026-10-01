"""Isolated HTTP client for the Profile Service (owned by another teammate).

All HTTP communication with the Profile Service lives here so that route
handlers and application services never make network calls directly. The
Profile Service base URL is always read from configuration.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

from app.core.config import Settings
from app.core.exceptions import ExternalServiceError, NotFoundError

logger = logging.getLogger(__name__)


class ProfileServiceClient:
    """Thin async client around the Profile Service REST API."""

    def __init__(self, settings: Settings):
        self._base_url = settings.PROFILE_SERVICE_URL.rstrip("/")
        self._timeout = settings.PROFILE_SERVICE_TIMEOUT_SECONDS

    async def get_job_posting(self, job_posting_id: str, auth_token: Optional[str] = None) -> dict[str, Any]:
        return await self._get(f"/api/v1/job-postings/{job_posting_id}", auth_token)

    async def get_cv(self, cv_id: str, auth_token: Optional[str] = None) -> dict[str, Any]:
        return await self._get(f"/api/v1/cvs/{cv_id}", auth_token)

    async def get_latest_cv(self, user_id: str, auth_token: Optional[str] = None) -> dict[str, Any]:
        """Fetch the caller's most recent CV, per the agreed Profile Service contract.

        The user is identified by the forwarded Authorization token, so the
        `user_id` is not part of the path.
        """
        return await self._get("/api/v1/cvs/latest", auth_token)

    async def _get(self, path: str, auth_token: Optional[str]) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url, headers=headers)
        except httpx.HTTPError as exc:
            logger.warning("Profile Service call failed: %s %s (%s)", "GET", url, exc)
            raise ExternalServiceError(
                "Could not reach the Profile Service", service="profile-service"
            ) from exc

        if response.status_code == 404:
            raise NotFoundError("Requested resource was not found in the Profile Service")
        if response.status_code >= 400:
            logger.warning(
                "Profile Service returned error status %s for %s", response.status_code, url
            )
            raise ExternalServiceError(
                "The Profile Service returned an unexpected error",
                service="profile-service",
                status_code=response.status_code,
            )

        return response.json()
