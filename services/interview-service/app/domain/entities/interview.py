"""Domain entities for interview sessions (framework-agnostic)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from app.domain.enums.interview_status import (
    InterviewStatus,
    QuestionAttemptStatus,
    QuestionSource,
)


@dataclass
class QuestionAttempt:
    """A single question as it exists within a specific interview session."""

    question_id: str
    order: int
    text: str
    category: str
    source: QuestionSource
    time_limit_seconds: int
    status: QuestionAttemptStatus = QuestionAttemptStatus.PENDING
    question_started_at: Optional[datetime] = None
    answered_at: Optional[datetime] = None
    answer_text: Optional[str] = None
    elapsed_seconds: Optional[int] = None


@dataclass
class ProfileSnapshot:
    """Immutable snapshot of CV/job-posting data captured at interview creation.

    Captured so that historical interviews remain consistent even if the
    Profile Service is unavailable or its data changes later.
    """

    job_posting_id: Optional[str] = None
    cv_id: Optional[str] = None
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    cv_summary: Optional[str] = None
    raw_job_posting: dict[str, Any] = field(default_factory=dict)
    raw_cv: dict[str, Any] = field(default_factory=dict)


@dataclass
class FeedbackReport:
    summary: str
    overall_score: float
    strengths: list[str] = field(default_factory=list)
    improvements: list[str] = field(default_factory=list)
    per_question_feedback: list[dict[str, Any]] = field(default_factory=list)
    generated_at: Optional[datetime] = None


@dataclass
class InterviewSession:
    id: str
    user_id: str
    title: str
    status: InterviewStatus
    profile_snapshot: ProfileSnapshot
    questions: list[QuestionAttempt] = field(default_factory=list)
    current_question_index: int = 0
    feedback: Optional[FeedbackReport] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # --- Domain behavior -------------------------------------------------

    def ensure_owner(self, user_id: str) -> None:
        from app.core.exceptions import ForbiddenError

        if self.user_id != user_id:
            raise ForbiddenError("You do not have access to this interview session")

    @property
    def current_question(self) -> Optional[QuestionAttempt]:
        if 0 <= self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None

    def find_question(self, question_id: str) -> Optional[QuestionAttempt]:
        for q in self.questions:
            if q.question_id == question_id:
                return q
        return None

    @property
    def is_terminal(self) -> bool:
        return self.status in (InterviewStatus.COMPLETED, InterviewStatus.ABANDONED)
