"""Business logic for question pool management."""
from __future__ import annotations

from typing import Optional

from app.application.schemas.common import PaginatedResponse, PaginationMeta
from app.application.schemas.question_schemas import (
    QuestionCreateRequest,
    QuestionResponse,
    QuestionUpdateRequest,
)
from app.core.exceptions import NotFoundError
from app.domain.entities.question import Question
from app.domain.enums.interview_status import QuestionDifficulty, QuestionStatus
from app.domain.repositories.question_repository import QuestionRepository


class QuestionService:
    """Encapsulates all question-pool business rules.

    Kept intentionally separate from interview lifecycle logic (see
    InterviewService) as required by the project spec.
    """

    def __init__(self, question_repository: QuestionRepository):
        self._repo = question_repository

    async def create_question(self, payload: QuestionCreateRequest, created_by: str) -> QuestionResponse:
        question = Question(
            id="",
            text=payload.text,
            category=payload.category,
            difficulty=payload.difficulty,
            tags=payload.tags,
            time_limit_seconds=payload.time_limit_seconds,
            status=QuestionStatus.ACTIVE,
            created_by=created_by,
        )
        created = await self._repo.create(question)
        return QuestionResponse.model_validate(created, from_attributes=True)

    async def get_question(self, question_id: str) -> QuestionResponse:
        question = await self._repo.get_by_id(question_id)
        if question is None:
            raise NotFoundError(f"Question {question_id} not found")
        return QuestionResponse.model_validate(question, from_attributes=True)

    async def list_questions(
        self,
        *,
        category: Optional[str] = None,
        difficulty: Optional[QuestionDifficulty] = None,
        status: Optional[QuestionStatus] = None,
        tag: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> PaginatedResponse[QuestionResponse]:
        questions, total = await self._repo.list(
            category=category,
            difficulty=difficulty,
            status=status,
            tag=tag,
            skip=skip,
            limit=limit,
        )
        items = [QuestionResponse.model_validate(q, from_attributes=True) for q in questions]
        return PaginatedResponse(items=items, pagination=PaginationMeta(total=total, skip=skip, limit=limit))

    async def update_question(self, question_id: str, payload: QuestionUpdateRequest) -> QuestionResponse:
        question = await self._repo.get_by_id(question_id)
        if question is None:
            raise NotFoundError(f"Question {question_id} not found")

        if payload.text is not None:
            question.text = payload.text
        if payload.category is not None:
            question.category = payload.category
        if payload.difficulty is not None:
            question.difficulty = payload.difficulty
        if payload.tags is not None:
            question.tags = payload.tags
        if payload.time_limit_seconds is not None:
            question.time_limit_seconds = payload.time_limit_seconds

        updated = await self._repo.update(question)
        return QuestionResponse.model_validate(updated, from_attributes=True)

    async def archive_question(self, question_id: str) -> QuestionResponse:
        archived = await self._repo.archive(question_id)
        if archived is None:
            raise NotFoundError(f"Question {question_id} not found")
        return QuestionResponse.model_validate(archived, from_attributes=True)
