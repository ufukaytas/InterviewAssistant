"""Repository-level unit tests, isolated from the HTTP layer.

Exercises the Mongo repository implementations directly against an
in-memory `mongomock_motor` database, so persistence behavior is verified
without booting the full FastAPI app or a real MongoDB instance.
"""
from __future__ import annotations

import pytest
import pytest_asyncio
from mongomock_motor import AsyncMongoMockClient

from app.domain.entities.interview import InterviewSession, ProfileSnapshot
from app.domain.entities.question import Question
from app.domain.enums.interview_status import InterviewStatus, QuestionDifficulty
from app.infrastructure.repositories.mongo_interview_repository import MongoInterviewRepository
from app.infrastructure.repositories.mongo_question_repository import MongoQuestionRepository

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def db():
    client = AsyncMongoMockClient()
    yield client["test_interview_db"]


async def test_question_repository_create_and_get(db):
    repo = MongoQuestionRepository(db)
    question = Question(id="", text="Why do you want this role?", category="behavioral", difficulty=QuestionDifficulty.EASY)

    created = await repo.create(question)
    assert created.id  # a UUID was assigned
    assert created.created_at is not None

    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.text == "Why do you want this role?"


async def test_question_repository_archive_is_soft_delete(db):
    repo = MongoQuestionRepository(db)
    question = await repo.create(
        Question(id="", text="Explain caching.", category="technical", difficulty=QuestionDifficulty.MEDIUM)
    )

    archived = await repo.archive(question.id)
    assert archived is not None
    assert archived.status.value == "archived"

    # The record still exists; it was archived, not physically deleted.
    still_there = await repo.get_by_id(question.id)
    assert still_there is not None
    assert still_there.status.value == "archived"


async def test_question_repository_list_filters_by_category(db):
    repo = MongoQuestionRepository(db)
    await repo.create(Question(id="", text="Q1", category="technical", difficulty=QuestionDifficulty.EASY))
    await repo.create(Question(id="", text="Q2", category="behavioral", difficulty=QuestionDifficulty.EASY))

    results, total = await repo.list(category="technical", skip=0, limit=10)
    assert total == 1
    assert results[0].category == "technical"


async def test_interview_repository_create_and_ownership_scoping(db):
    repo = MongoInterviewRepository(db)
    session_a = InterviewSession(
        id="",
        user_id="user-a",
        title="A's interview",
        status=InterviewStatus.CREATED,
        profile_snapshot=ProfileSnapshot(),
    )
    session_b = InterviewSession(
        id="",
        user_id="user-b",
        title="B's interview",
        status=InterviewStatus.CREATED,
        profile_snapshot=ProfileSnapshot(),
    )
    await repo.create(session_a)
    await repo.create(session_b)

    results, total = await repo.list_for_user("user-a", skip=0, limit=10)
    assert total == 1
    assert results[0].user_id == "user-a"


async def test_interview_repository_update_persists_status_change(db):
    repo = MongoInterviewRepository(db)
    session = await repo.create(
        InterviewSession(
            id="",
            user_id="user-a",
            title="Test",
            status=InterviewStatus.CREATED,
            profile_snapshot=ProfileSnapshot(),
        )
    )

    session.status = InterviewStatus.IN_PROGRESS
    await repo.update(session)

    reloaded = await repo.get_by_id(session.id)
    assert reloaded is not None
    assert reloaded.status == InterviewStatus.IN_PROGRESS


async def test_interview_repository_delete(db):
    repo = MongoInterviewRepository(db)
    session = await repo.create(
        InterviewSession(
            id="",
            user_id="user-a",
            title="Test",
            status=InterviewStatus.CREATED,
            profile_snapshot=ProfileSnapshot(),
        )
    )

    deleted = await repo.delete(session.id)
    assert deleted is True
    assert await repo.get_by_id(session.id) is None
