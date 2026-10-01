"""Tests for the system endpoints: /health, /ready, /dev/token."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_health_is_always_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_ready_reports_mongodb_connected(client):
    response = await client.get("/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["mongodb"] == "connected"


async def test_dev_token_issues_valid_jwt(client):
    response = await client.post("/dev/token", json={"user_id": "user-42"})
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"

    # The issued token must actually authenticate against a protected route.
    me_response = await client.get(
        "/api/v1/interviews", headers={"Authorization": f"Bearer {body['access_token']}"}
    )
    assert me_response.status_code == 200


async def test_dev_token_disabled_in_production(client, monkeypatch):
    from app.api.dependencies import settings as settings_dep

    settings = settings_dep.get_app_settings()
    monkeypatch.setattr(settings, "APP_ENV", "production")

    response = await client.post("/dev/token", json={"user_id": "user-1"})
    assert response.status_code == 403
