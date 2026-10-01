"""Tests for the Question Pool API."""
from __future__ import annotations

import pytest

from .conftest import auth_headers

pytestmark = pytest.mark.asyncio

USER_HEADERS = auth_headers("user-1")


async def _create_question(client, text="Tell me about yourself.", category="general", **overrides):
    payload = {"text": text, "category": category, "difficulty": "medium", "time_limit_seconds": 90}
    payload.update(overrides)
    response = await client.post("/api/v1/questions", json=payload, headers=USER_HEADERS)
    assert response.status_code == 201
    return response.json()


async def test_create_and_get_question(client):
    created = await _create_question(client, text="What is a REST API?", category="technical")
    response = await client.get(f"/api/v1/questions/{created['id']}", headers=USER_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "What is a REST API?"
    assert body["status"] == "active"


async def test_get_unknown_question_returns_404(client):
    response = await client.get("/api/v1/questions/does-not-exist", headers=USER_HEADERS)
    assert response.status_code == 404


async def test_list_questions_filters_by_category(client):
    await _create_question(client, text="Explain polymorphism.", category="technical")
    await _create_question(client, text="Tell me about a conflict you resolved.", category="behavioral")

    response = await client.get(
        "/api/v1/questions", params={"category": "technical"}, headers=USER_HEADERS
    )
    assert response.status_code == 200
    body = response.json()
    assert all(item["category"] == "technical" for item in body["items"])
    assert body["pagination"]["limit"] > 0


async def test_update_question(client):
    created = await _create_question(client)
    response = await client.patch(
        f"/api/v1/questions/{created['id']}",
        json={"text": "Updated question text", "time_limit_seconds": 60},
        headers=USER_HEADERS,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "Updated question text"
    assert body["time_limit_seconds"] == 60


async def test_delete_archives_instead_of_removing(client):
    created = await _create_question(client)

    delete_response = await client.delete(f"/api/v1/questions/{created['id']}", headers=USER_HEADERS)
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "archived"

    # The question must still be retrievable (soft-delete, not a hard delete).
    get_response = await client.get(f"/api/v1/questions/{created['id']}", headers=USER_HEADERS)
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "archived"
