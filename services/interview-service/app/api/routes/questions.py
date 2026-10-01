"""Question Pool API routes. Thin controllers only: no business logic here."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import CurrentUser, get_current_user
from app.api.dependencies.pagination import PaginationParams, get_pagination_params
from app.api.dependencies.services import get_question_service
from app.application.schemas.common import PaginatedResponse
from app.application.schemas.question_schemas import (
    QuestionCreateRequest,
    QuestionResponse,
    QuestionUpdateRequest,
)
from app.application.services.question_service import QuestionService
from app.domain.enums.interview_status import QuestionDifficulty, QuestionStatus

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("", response_model=PaginatedResponse[QuestionResponse])
async def list_questions(
    category: Optional[str] = Query(default=None),
    difficulty: Optional[QuestionDifficulty] = Query(default=None),
    status_filter: Optional[QuestionStatus] = Query(default=None, alias="status"),
    tag: Optional[str] = Query(default=None),
    pagination: PaginationParams = Depends(get_pagination_params),
    _: CurrentUser = Depends(get_current_user),
    service: QuestionService = Depends(get_question_service),
) -> PaginatedResponse[QuestionResponse]:
    return await service.list_questions(
        category=category,
        difficulty=difficulty,
        status=status_filter,
        tag=tag,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.post("", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    payload: QuestionCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: QuestionService = Depends(get_question_service),
) -> QuestionResponse:
    return await service.create_question(payload, created_by=current_user.user_id)


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: str,
    _: CurrentUser = Depends(get_current_user),
    service: QuestionService = Depends(get_question_service),
) -> QuestionResponse:
    return await service.get_question(question_id)


@router.patch("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: str,
    payload: QuestionUpdateRequest,
    _: CurrentUser = Depends(get_current_user),
    service: QuestionService = Depends(get_question_service),
) -> QuestionResponse:
    return await service.update_question(question_id, payload)


@router.delete("/{question_id}", response_model=QuestionResponse)
async def archive_question(
    question_id: str,
    _: CurrentUser = Depends(get_current_user),
    service: QuestionService = Depends(get_question_service),
) -> QuestionResponse:
    """Archives (soft-deletes) the question rather than removing it physically."""
    return await service.archive_question(question_id)
