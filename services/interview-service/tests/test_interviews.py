"""Tests for the Interview Lifecycle API."""
from __future__ import annotations

import pytest

from .conftest import auth_headers

pytestmark = pytest.mark.asyncio

SEEDER_HEADERS = auth_headers("seeder-1")
OWNER_HEADERS = auth_headers("owner-1")
OTHER_USER_HEADERS = auth_headers("other-user")


async def _seed_pool_questions(client, count=3):
    for i in range(count):
        response = await client.post(
            "/api/v1/questions",
            json={
                "text": f"Pool question number {i}",
                "category": "general",
                "time_limit_seconds": 60,
            },
            headers=SEEDER_HEADERS,
        )
        assert response.status_code == 201


async def _create_interview(client, headers=OWNER_HEADERS, **overrides):
    payload = {"title": "Backend Engineer Practice Round", "question_count": 3}
    payload.update(overrides)
    response = await client.post("/api/v1/interviews", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


async def test_create_interview_from_pool_snapshots_profile(client):
    await _seed_pool_questions(client, count=3)
    interview = await _create_interview(
        client, job_posting_id="job-123", cv_id="cv-456"
    )
    assert interview["status"] == "created"
    assert len(interview["questions"]) == 3
    assert interview["profile_snapshot"]["job_posting_id"] == "job-123"
    # Snapshot data comes from the (mocked) Profile Service at creation time.
    assert interview["profile_snapshot"]["job_title"] == "Backend Engineer"


async def test_create_interview_fails_without_available_questions(client):
    # No pool questions seeded and generation disabled -> nothing to build.
    response = await client.post(
        "/api/v1/interviews",
        json={"title": "Empty", "question_count": 3, "use_generated_questions": False},
        headers=OWNER_HEADERS,
    )
    assert response.status_code == 422


async def test_create_interview_with_generated_questions(client):
    response = await client.post(
        "/api/v1/interviews",
        json={"title": "Generated round", "question_count": 2, "use_generated_questions": True},
        headers=OWNER_HEADERS,
    )
    assert response.status_code == 201
    body = response.json()
    assert len(body["questions"]) == 2
    assert all(q["source"] == "generated" for q in body["questions"])


async def test_user_cannot_access_another_users_interview(client):
    await _seed_pool_questions(client)
    interview = await _create_interview(client, headers=OWNER_HEADERS)

    response = await client.get(
        f"/api/v1/interviews/{interview['id']}", headers=OTHER_USER_HEADERS
    )
    assert response.status_code == 403


async def test_owner_can_access_own_interview(client):
    await _seed_pool_questions(client)
    interview = await _create_interview(client, headers=OWNER_HEADERS)

    response = await client.get(
        f"/api/v1/interviews/{interview['id']}", headers=OWNER_HEADERS
    )
    assert response.status_code == 200
    assert response.json()["id"] == interview["id"]


async def test_get_unknown_interview_returns_404(client):
    response = await client.get("/api/v1/interviews/does-not-exist", headers=OWNER_HEADERS)
    assert response.status_code == 404


async def test_list_interviews_is_paginated_and_scoped_to_user(client):
    await _seed_pool_questions(client)
    await _create_interview(client, headers=OWNER_HEADERS, title="Round 1")
    await _create_interview(client, headers=OWNER_HEADERS, title="Round 2")
    await _create_interview(client, headers=OTHER_USER_HEADERS, title="Someone else's")

    response = await client.get(
        "/api/v1/interviews", params={"limit": 1, "skip": 0}, headers=OWNER_HEADERS
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["pagination"]["total"] == 2  # Only the owner's interviews are counted.


async def test_start_interview_transitions_to_in_progress(client):
    await _seed_pool_questions(client)
    interview = await _create_interview(client, headers=OWNER_HEADERS)

    response = await client.post(
        f"/api/v1/interviews/{interview['id']}/start", headers=OWNER_HEADERS
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "in_progress"
    assert body["started_at"] is not None
    assert body["questions"][0]["status"] == "in_progress"


async def test_cannot_start_interview_twice(client):
    await _seed_pool_questions(client)
    interview = await _create_interview(client, headers=OWNER_HEADERS)
    await client.post(f"/api/v1/interviews/{interview['id']}/start", headers=OWNER_HEADERS)

    second_start = await client.post(
        f"/api/v1/interviews/{interview['id']}/start", headers=OWNER_HEADERS
    )
    assert second_start.status_code == 409


async def test_answer_question_persists_answer_and_elapsed_time(client):
    await _seed_pool_questions(client)
    interview = await _create_interview(client, headers=OWNER_HEADERS)
    await client.post(f"/api/v1/interviews/{interview['id']}/start", headers=OWNER_HEADERS)

    first_question_id = interview["questions"][0]["question_id"]
    response = await client.post(
        f"/api/v1/interviews/{interview['id']}/questions/{first_question_id}/answer",
        json={"answer_text": "My answer to this question."},
        headers=OWNER_HEADERS,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "answered"
    assert body["answer_text"] == "My answer to this question."
    assert body["elapsed_seconds"] is not None
    assert body["question_started_at"] is not None
    assert body["answered_at"] is not None


async def test_skip_question_marks_it_skipped(client):
    await _seed_pool_questions(client)
    interview = await _create_interview(client, headers=OWNER_HEADERS)
    await client.post(f"/api/v1/interviews/{interview['id']}/start", headers=OWNER_HEADERS)

    first_question_id = interview["questions"][0]["question_id"]
    response = await client.post(
        f"/api/v1/interviews/{interview['id']}/questions/{first_question_id}/skip",
        headers=OWNER_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "skipped"


async def test_cannot_answer_question_before_interview_starts(client):
    await _seed_pool_questions(client)
    interview = await _create_interview(client, headers=OWNER_HEADERS)
    first_question_id = interview["questions"][0]["question_id"]

    response = await client.post(
        f"/api/v1/interviews/{interview['id']}/questions/{first_question_id}/answer",
        json={"answer_text": "Too early."},
        headers=OWNER_HEADERS,
    )
    assert response.status_code == 409


async def test_answer_unknown_question_returns_404(client):
    await _seed_pool_questions(client)
    interview = await _create_interview(client, headers=OWNER_HEADERS)
    await client.post(f"/api/v1/interviews/{interview['id']}/start", headers=OWNER_HEADERS)

    response = await client.post(
        f"/api/v1/interviews/{interview['id']}/questions/does-not-exist/answer",
        json={"answer_text": "N/A"},
        headers=OWNER_HEADERS,
    )
    assert response.status_code == 404


async def test_complete_interview_generates_feedback(client):
    await _seed_pool_questions(client)
    interview = await _create_interview(client, headers=OWNER_HEADERS, question_count=2)
    await client.post(f"/api/v1/interviews/{interview['id']}/start", headers=OWNER_HEADERS)

    for q in interview["questions"]:
        await client.post(
            f"/api/v1/interviews/{interview['id']}/questions/{q['question_id']}/answer",
            json={"answer_text": "An answer."},
            headers=OWNER_HEADERS,
        )

    response = await client.post(
        f"/api/v1/interviews/{interview['id']}/complete", headers=OWNER_HEADERS
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["completed_at"] is not None
    assert body["feedback"] is not None
    assert body["feedback"]["overall_score"] == 100.0

    feedback_response = await client.get(
        f"/api/v1/interviews/{interview['id']}/feedback", headers=OWNER_HEADERS
    )
    assert feedback_response.status_code == 200
    assert feedback_response.json()["summary"]


async def test_cannot_complete_interview_that_never_started(client):
    await _seed_pool_questions(client)
    interview = await _create_interview(client, headers=OWNER_HEADERS)

    response = await client.post(
        f"/api/v1/interviews/{interview['id']}/complete", headers=OWNER_HEADERS
    )
    assert response.status_code == 409


async def test_feedback_not_found_before_completion(client):
    await _seed_pool_questions(client)
    interview = await _create_interview(client, headers=OWNER_HEADERS)

    response = await client.get(
        f"/api/v1/interviews/{interview['id']}/feedback", headers=OWNER_HEADERS
    )
    assert response.status_code == 404


async def test_delete_in_progress_interview_marks_it_abandoned(client):
    await _seed_pool_questions(client)
    interview = await _create_interview(client, headers=OWNER_HEADERS)
    await client.post(f"/api/v1/interviews/{interview['id']}/start", headers=OWNER_HEADERS)

    delete_response = await client.delete(
        f"/api/v1/interviews/{interview['id']}", headers=OWNER_HEADERS
    )
    assert delete_response.status_code == 204

    get_response = await client.get(
        f"/api/v1/interviews/{interview['id']}", headers=OWNER_HEADERS
    )
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "abandoned"


async def test_delete_created_interview_removes_it(client):
    await _seed_pool_questions(client)
    interview = await _create_interview(client, headers=OWNER_HEADERS)

    delete_response = await client.delete(
        f"/api/v1/interviews/{interview['id']}", headers=OWNER_HEADERS
    )
    assert delete_response.status_code == 204

    get_response = await client.get(
        f"/api/v1/interviews/{interview['id']}", headers=OWNER_HEADERS
    )
    assert get_response.status_code == 404
