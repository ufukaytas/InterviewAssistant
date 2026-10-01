"""Interview Lifecycle API routes. Thin controllers only: no business logic here."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.auth import CurrentUser, get_current_user
from app.api.dependencies.pagination import PaginationParams, get_pagination_params
from app.api.dependencies.services import get_interview_service
from app.application.schemas.common import PaginatedResponse
from app.application.schemas.interview_schemas import (
    AnswerSubmitRequest,
    CurrentQuestionResponse,
    FeedbackResponse,
    InterviewCreateRequest,
    InterviewDetailResponse,
    InterviewSummaryResponse,
    QuestionAttemptResponse,
)
from app.application.services.interview_service import InterviewService
from app.domain.enums.interview_status import InterviewStatus

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("", response_model=InterviewDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    payload: InterviewCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
) -> InterviewDetailResponse:
    return await service.create_interview(payload, user_id=user.user_id, auth_token=user.raw_token)


@router.get("", response_model=PaginatedResponse[InterviewSummaryResponse])
async def list_interviews(
    status_filter: Optional[InterviewStatus] = Query(default=None, alias="status"),
    pagination: PaginationParams = Depends(get_pagination_params),
    user: CurrentUser = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
) -> PaginatedResponse[InterviewSummaryResponse]:
    return await service.list_interviews(
        user.user_id, status=status_filter, skip=pagination.skip, limit=pagination.limit
    )


@router.get("/{session_id}", response_model=InterviewDetailResponse)
async def get_interview(
    session_id: str,
    user: CurrentUser = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
) -> InterviewDetailResponse:
    return await service.get_interview(session_id, user.user_id)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_interview(
    session_id: str,
    user: CurrentUser = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
) -> None:
    """Deletes a created/completed/abandoned interview, or marks an
    in-progress one as abandoned instead of deleting it outright."""
    await service.delete_interview(session_id, user.user_id)


@router.post("/{session_id}/start", response_model=InterviewDetailResponse)
async def start_interview(
    session_id: str,
    user: CurrentUser = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
) -> InterviewDetailResponse:
    return await service.start_interview(session_id, user.user_id)


@router.get("/{session_id}/current-question", response_model=CurrentQuestionResponse)
async def get_current_question(
    session_id: str,
    user: CurrentUser = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
) -> CurrentQuestionResponse:
    return await service.get_current_question(session_id, user.user_id)


@router.post(
    "/{session_id}/questions/{question_id}/start",
    response_model=QuestionAttemptResponse,
)
async def start_question(
    session_id: str,
    question_id: str,
    user: CurrentUser = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
) -> QuestionAttemptResponse:
    return await service.start_question(session_id, question_id, user.user_id)


@router.post(
    "/{session_id}/questions/{question_id}/answer",
    response_model=QuestionAttemptResponse,
)
async def answer_question(
    session_id: str,
    question_id: str,
    payload: AnswerSubmitRequest,
    user: CurrentUser = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
) -> QuestionAttemptResponse:
    return await service.answer_question(session_id, question_id, payload.answer_text, user.user_id)


@router.post(
    "/{session_id}/questions/{question_id}/skip",
    response_model=QuestionAttemptResponse,
)
async def skip_question(
    session_id: str,
    question_id: str,
    user: CurrentUser = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
) -> QuestionAttemptResponse:
    return await service.skip_question(session_id, question_id, user.user_id)


@router.post("/{session_id}/complete", response_model=InterviewDetailResponse)
async def complete_interview(
    session_id: str,
    user: CurrentUser = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
) -> InterviewDetailResponse:
    return await service.complete_interview(session_id, user.user_id)


@router.get("/{session_id}/feedback", response_model=FeedbackResponse)
async def get_feedback(
    session_id: str,
    user: CurrentUser = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
) -> FeedbackResponse:
    return await service.get_feedback(session_id, user.user_id)
