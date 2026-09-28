"""Tests for JWT authentication/authorization behavior."""
from __future__ import annotations

import jwt
import pytest

from app.core.config import get_settings

from .conftest import auth_headers

pytestmark = pytest.mark.asyncio


async def test_protected_route_without_token_is_unauthorized(client):
    response = await client.get("/api/v1/interviews")
    assert response.status_code == 401


async def test_protected_route_with_garbage_token_is_unauthorized(client):
    response = await client.get(
        "/api/v1/interviews", headers={"Authorization": "Bearer not-a-real-jwt"}
    )
    assert response.status_code == 401


async def test_protected_route_with_wrong_issuer_is_unauthorized(client):
    settings = get_settings()
    bad_token = jwt.encode(
        {"sub": "user-1", "iss": "someone-else", "aud": settings.JWT_AUDIENCE},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    response = await client.get(
        "/api/v1/interviews", headers={"Authorization": f"Bearer {bad_token}"}
    )
    assert response.status_code == 401


async def test_protected_route_with_wrong_secret_is_unauthorized(client):
    settings = get_settings()
    bad_token = jwt.encode(
        {"sub": "user-1", "iss": settings.JWT_ISSUER, "aud": settings.JWT_AUDIENCE},
        "totally-wrong-secret",
        algorithm=settings.JWT_ALGORITHM,
    )
    response = await client.get(
        "/api/v1/interviews", headers={"Authorization": f"Bearer {bad_token}"}
    )
    assert response.status_code == 401


async def test_question_write_endpoints_require_authentication(client):
    payload = {"text": "Describe your ideal team culture.", "category": "behavioral"}
    assert (await client.post("/api/v1/questions", json=payload)).status_code == 401
    assert (await client.patch("/api/v1/questions/x", json={"text": "y"})).status_code == 401
    assert (await client.delete("/api/v1/questions/x")).status_code == 401


async def test_any_authenticated_user_can_create_question(client):
    # No role system in v1: a valid token is enough.
    response = await client.post(
        "/api/v1/questions",
        json={"text": "Describe your ideal team culture.", "category": "behavioral"},
        headers=auth_headers("regular-user"),
    )
    assert response.status_code == 201
