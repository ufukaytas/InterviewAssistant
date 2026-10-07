"""Pydantic schemas for the Interview Lifecycle API."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.domain.enums.interview_status import (
    InterviewStatus,
    QuestionAttemptStatus,
    QuestionSource,
)


class InterviewCreateRequest(BaseModel):
    # Verilmezse (ya da boş gönderilirse) backend anlamlı bir başlık üretir:
    # önce Profile Service'ten gelen iş ilanı başlığı, yoksa tarih/saat.
    title: Optional[str] = Field(default=None, max_length=200)
    job_posting_id: Optional[str] = None
    cv_id: Optional[str] = None
    question_count: Optional[int] = Field(default=None, ge=1, le=50)
    use_generated_questions: bool = Field(
        default=False,
        description="If true, questions are generated via the LLM layer instead of the pool.",
    )
    category: Optional[str] = None


class AnswerSubmitRequest(BaseModel):
    answer_text: str = Field(min_length=1, max_length=20000)


class QuestionAttemptResponse(BaseModel):
    question_id: str
    order: int
    text: str
    category: str
    source: QuestionSource
    time_limit_seconds: int
    status: QuestionAttemptStatus
    question_started_at: Optional[datetime] = None
    answered_at: Optional[datetime] = None
    answer_text: Optional[str] = None
    elapsed_seconds: Optional[int] = None
    remaining_seconds: Optional[int] = None


class ProfileSnapshotResponse(BaseModel):
    job_posting_id: Optional[str] = None
    cv_id: Optional[str] = None
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    cv_summary: Optional[str] = None


class FeedbackResponse(BaseModel):
    summary: str
    overall_score: float
    strengths: list[str]
    improvements: list[str]
    per_question_feedback: list[dict]
    generated_at: Optional[datetime] = None


class InterviewSummaryResponse(BaseModel):
    """Lightweight representation used in list views."""

    id: str
    title: str
    status: InterviewStatus
    total_questions: int
    overall_score: Optional[float] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class InterviewDetailResponse(BaseModel):
    id: str
    user_id: str
    title: str
    status: InterviewStatus
    profile_snapshot: ProfileSnapshotResponse
    questions: list[QuestionAttemptResponse]
    current_question_index: int
    feedback: Optional[FeedbackResponse] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class CurrentQuestionResponse(BaseModel):
    question: Optional[QuestionAttemptResponse] = None
    is_last_question: bool = False
    interview_status: InterviewStatus
