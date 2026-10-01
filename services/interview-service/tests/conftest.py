"""Shared pytest fixtures.

Tests never touch a real MongoDB or a real Profile Service:
- MongoDB is swapped for `mongomock_motor`'s in-memory async client.
- The Profile Service client is swapped for a fake, in-process stub.

This keeps the whole suite fast, deterministic, and runnable offline, as
required by the project spec.
"""
from __future__ import annotations

from typing import Any, AsyncIterator

import httpx
import pytest
import pytest_asyncio
from mongomock_motor import AsyncMongoMockClient

import app.infrastructure.database.mongodb as mongodb_module
from app.api.dependencies.services import get_profile_service_client
from app.core.config import get_settings
from app.core.security import create_dev_access_token
from app.main import app, lifespan


class FakeProfileServiceClient:
    """In-process stand-in for the real Profile Service HTTP client."""

    async def get_job_posting(self, job_posting_id: str, auth_token: str | None = None) -> dict[str, Any]:
        return {
            "id": job_posting_id,
            "title": "Backend Engineer",
            "description": "Build and maintain backend services.",
        }

    async def get_cv(self, cv_id: str, auth_token: str | None = None) -> dict[str, Any]:
        return {"id": cv_id, "summary": "5 years of backend development experience."}

    async def get_latest_cv(self, user_id: str, auth_token: str | None = None) -> dict[str, Any]:
        return {"id": "latest-cv", "summary": "5 years of backend development experience."}


@pytest_asyncio.fixture
async def client(monkeypatch) -> AsyncIterator[httpx.AsyncClient]:
    """An httpx AsyncClient wired to the FastAPI app with mocked infrastructure."""
    # Swap the real Motor client for an in-memory mock before the app's
    # lifespan connects to "MongoDB".
    monkeypatch.setattr(mongodb_module, "AsyncIOMotorClient", AsyncMongoMockClient)

    app.dependency_overrides[get_profile_service_client] = lambda: FakeProfileServiceClient()
    get_settings.cache_clear()

    async with lifespan(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
            yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def settings():
    return get_settings()


def auth_headers(user_id: str = "user-1") -> dict[str, str]:
    """Build a valid Authorization header signed exactly like the Auth Service would."""
    token = create_dev_access_token(get_settings(), subject=user_id)
    return {"Authorization": f"Bearer {token}"}
