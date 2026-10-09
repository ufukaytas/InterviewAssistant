"""Business logic for the interview lifecycle.

All state transitions, server-side timing, ownership checks and orchestration
between the question pool, the Profile Service snapshot and the LLM layer
live here. Route handlers only translate HTTP <-> this service.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from app.application.schemas.common import PaginatedResponse, PaginationMeta
from app.application.schemas.interview_schemas import (
    CurrentQuestionResponse,
    FeedbackResponse,
    InterviewCreateRequest,
    InterviewDetailResponse,
    InterviewSummaryResponse,
    ProfileSnapshotResponse,
    QuestionAttemptResponse,
)
from app.core.config import Settings
from app.core.exceptions import (
    ForbiddenError,
    InvalidStateTransitionError,
    NotFoundError,
    ValidationAppError,
)
from app.domain.entities.interview import (
    FeedbackReport,
    InterviewSession,
    ProfileSnapshot,
    QuestionAttempt,
)
from app.domain.enums.interview_status import (
    InterviewStatus,
    QuestionAttemptStatus,
    QuestionSource,
)
from app.domain.repositories.interview_repository import InterviewRepository
from app.domain.repositories.question_repository import QuestionRepository
from app.infrastructure.external_clients.llm_client import LLMClient
from app.infrastructure.external_clients.profile_service_client import (
    ProfileServiceClient,
)


class InterviewService:
    def __init__(
        self,
        interview_repository: InterviewRepository,
        question_repository: QuestionRepository,
        profile_client: ProfileServiceClient,
        llm_client: LLMClient,
        settings: Settings,
    ):
        self._interviews = interview_repository
        self._questions = question_repository
        self._profile_client = profile_client
        self._llm = llm_client
        self._settings = settings

    # --- Creation ----------------------------------------------------

    async def create_interview(
        self,
        payload: InterviewCreateRequest,
        user_id: str,
        auth_token: Optional[str],
    ) -> InterviewDetailResponse:
        snapshot = await self._build_profile_snapshot(
            payload,
            user_id,
            auth_token,
        )

        question_count = (
            payload.question_count
            or self._settings.DEFAULT_INTERVIEW_QUESTION_COUNT
        )

        if payload.use_generated_questions:
            attempts = await self._generate_question_attempts(
                snapshot,
                question_count,
            )
        else:
            attempts = await self._pick_pool_question_attempts(
                payload.category,
                question_count,
            )

        if not attempts:
            raise ValidationAppError(
                "No questions are available to build this interview. "
                "Add questions to the pool or enable generated questions."
            )

        title = (payload.title or "").strip() or self._default_interview_title(snapshot)

        interview = InterviewSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            status=InterviewStatus.CREATED,
            profile_snapshot=snapshot,
            questions=attempts,
        )

        created = await self._interviews.create(interview)
        return self._to_detail_response(created)

    @staticmethod
    def _default_interview_title(snapshot: ProfileSnapshot) -> str:
        """Title verilmediğinde kullanılır: önce iş ilanı başlığı, yoksa tarih/saat."""
        if snapshot.job_title:
            return f"{snapshot.job_title} Mulakati"
        now = datetime.now(timezone.utc)
        return f"Mulakat - {now.strftime('%d.%m.%Y %H:%M')}"

    async def _build_profile_snapshot(
        self,
        payload: InterviewCreateRequest,
        user_id: str,
        auth_token: Optional[str],
    ) -> ProfileSnapshot:
        """Fetch CV/job data from the Profile Service and freeze it as a snapshot.

        The interview must not depend on the Profile Service being reachable
        later, so failures here only affect creation, never historical reads.
        """
        job_posting_raw: dict = {}
        cv_raw: dict = {}

        if payload.job_posting_id:
            job_posting_raw = await self._profile_client.get_job_posting(
                payload.job_posting_id,
                auth_token,
            )

        if payload.cv_id:
            cv_raw = await self._profile_client.get_cv(
                payload.cv_id,
                auth_token,
            )
        else:
            # No explicit cv_id: best-effort fetch of the user's latest CV,
            # regardless of whether a job_posting_id was supplied.
            try:
                cv_raw = await self._profile_client.get_latest_cv(
                    user_id,
                    auth_token,
                )
            except Exception:  # noqa: BLE001 - snapshot fetch is best-effort
                cv_raw = {}

        max_chars = self._settings.PROFILE_TEXT_MAX_CHARS

        return ProfileSnapshot(
            job_posting_id=payload.job_posting_id,
            cv_id=payload.cv_id,
            job_title=job_posting_raw.get("title"),
            job_description=self._truncate_text(
                job_posting_raw.get("description"),
                max_chars,
            ),
            cv_summary=self._truncate_text(
                cv_raw.get("summary"),
                max_chars,
            ),
            raw_job_posting=job_posting_raw,
            raw_cv=cv_raw,
        )

    @staticmethod
    def _truncate_text(
        value: object,
        max_chars: int,
    ) -> Optional[str]:
        """Cap externally supplied free text so LLM cost/latency stay bounded."""
        if value is None:
            return None

        text = value if isinstance(value, str) else str(value)

        return text if len(text) <= max_chars else text[:max_chars]

    async def _pick_pool_question_attempts(
        self,
        category: Optional[str],
        count: int,
    ) -> list[QuestionAttempt]:
        questions = await self._questions.list_random_pool(
            category=category,
            count=count,
        )

        return [
            QuestionAttempt(
                question_id=q.id,
                order=i,
                text=q.text,
                category=q.category,
                source=QuestionSource.POOL,
                time_limit_seconds=q.time_limit_seconds,
            )
            for i, q in enumerate(questions)
        ]

    async def _generate_question_attempts(
        self,
        snapshot: ProfileSnapshot,
        count: int,
    ) -> list[QuestionAttempt]:
        generated = await self._llm.generate_questions(
            job_title=snapshot.job_title or "",
            job_description=snapshot.job_description or "",
            cv_summary=snapshot.cv_summary or "",
            count=count,
        )

        return [
            QuestionAttempt(
                question_id=str(uuid.uuid4()),
                order=i,
                text=item["text"],
                category=item.get("category", "general"),
                source=QuestionSource.GENERATED,
                time_limit_seconds=(
                    self._settings.DEFAULT_QUESTION_TIME_LIMIT_SECONDS
                ),
            )
            for i, item in enumerate(generated)
        ]

    # --- Retrieval -----------------------------------------------------

    async def get_interview(
        self,
        session_id: str,
        user_id: str,
    ) -> InterviewDetailResponse:
        interview = await self._get_owned_interview(
            session_id,
            user_id,
        )
        return self._to_detail_response(interview)

    async def list_interviews(
        self,
        user_id: str,
        *,
        status: Optional[InterviewStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> PaginatedResponse[InterviewSummaryResponse]:
        interviews, total = await self._interviews.list_for_user(
            user_id,
            status=status,
            skip=skip,
            limit=limit,
        )

        items = [
            self._to_summary_response(i)
            for i in interviews
        ]

        return PaginatedResponse(
            items=items,
            pagination=PaginationMeta(
                total=total,
                skip=skip,
                limit=limit,
            ),
        )

    async def delete_interview(
        self,
        session_id: str,
        user_id: str,
    ) -> None:
        interview = await self._get_owned_interview(
            session_id,
            user_id,
        )

        if interview.status == InterviewStatus.IN_PROGRESS:
            interview.status = InterviewStatus.ABANDONED
            interview.completed_at = datetime.now(timezone.utc)
            await self._interviews.update(interview)
        else:
            deleted = await self._interviews.delete(session_id)

            if not deleted:
                raise NotFoundError(
                    f"Interview session {session_id} not found"
                )

    # --- Lifecycle transitions ------------------------------------------

    async def start_interview(
        self,
        session_id: str,
        user_id: str,
    ) -> InterviewDetailResponse:
        interview = await self._get_owned_interview(
            session_id,
            user_id,
        )

        if interview.status != InterviewStatus.CREATED:
            raise InvalidStateTransitionError(
                f"Cannot start an interview in status "
                f"'{interview.status.value}'"
            )

        now = datetime.now(timezone.utc)

        interview.status = InterviewStatus.IN_PROGRESS
        interview.started_at = now
        interview.current_question_index = 0

        if interview.questions:
            interview.questions[0].status = (
                QuestionAttemptStatus.IN_PROGRESS
            )
            interview.questions[0].question_started_at = now

        updated = await self._interviews.update(interview)

        return self._to_detail_response(updated)

    async def get_current_question(
        self,
        session_id: str,
        user_id: str,
    ) -> CurrentQuestionResponse:
        interview = await self._get_owned_interview(
            session_id,
            user_id,
        )

        current = interview.current_question

        is_last = (
            interview.current_question_index
            == len(interview.questions) - 1
        )

        return CurrentQuestionResponse(
            question=(
                self._to_attempt_response(current)
                if current
                else None
            ),
            is_last_question=is_last,
            interview_status=interview.status,
        )

    async def start_question(
        self,
        session_id: str,
        question_id: str,
        user_id: str,
    ) -> QuestionAttemptResponse:
        interview = await self._get_owned_interview(
            session_id,
            user_id,
        )

        self._ensure_in_progress(interview)

        attempt = self._get_question_or_404(
            interview,
            question_id,
        )

        if attempt.status not in (
            QuestionAttemptStatus.PENDING,
            QuestionAttemptStatus.IN_PROGRESS,
        ):
            raise InvalidStateTransitionError(
                f"Question '{question_id}' cannot be started "
                f"from status '{attempt.status.value}'"
            )

        if attempt.question_started_at is None:
            attempt.question_started_at = datetime.now(timezone.utc)

        attempt.status = QuestionAttemptStatus.IN_PROGRESS

        await self._interviews.update(interview)

        return self._to_attempt_response(attempt)

    async def answer_question(
        self,
        session_id: str,
        question_id: str,
        answer_text: str,
        user_id: str,
    ) -> QuestionAttemptResponse:
        interview = await self._get_owned_interview(
            session_id,
            user_id,
        )

        self._ensure_in_progress(interview)

        attempt = self._get_question_or_404(
            interview,
            question_id,
        )

        if attempt.status not in (
            QuestionAttemptStatus.PENDING,
            QuestionAttemptStatus.IN_PROGRESS,
        ):
            raise InvalidStateTransitionError(
                f"Question '{question_id}' cannot be answered "
                f"from status '{attempt.status.value}'"
            )

        now = datetime.now(timezone.utc)
        started_at = attempt.question_started_at or now

        elapsed = (now - started_at).total_seconds()
        if attempt.time_limit_seconds and elapsed > attempt.time_limit_seconds:
            attempt.status = QuestionAttemptStatus.EXPIRED  # veya doğrudan hataya düş
            await self._interviews.update(interview)
            raise ValidationAppError(
                "Soru için ayrılan süre dolduğundan cevabınız kabul edilmedi."
            )

        attempt.question_started_at = started_at
        attempt.answered_at = now
        attempt.answer_text = answer_text
        attempt.elapsed_seconds = max(
            0,
            int(elapsed),
        )
        attempt.status = QuestionAttemptStatus.ANSWERED

        self._advance_to_next_pending(interview)

        await self._interviews.update(interview)

        return self._to_attempt_response(attempt)

    async def skip_question(
        self,
        session_id: str,
        question_id: str,
        user_id: str,
    ) -> QuestionAttemptResponse:
        interview = await self._get_owned_interview(
            session_id,
            user_id,
        )

        self._ensure_in_progress(interview)

        attempt = self._get_question_or_404(
            interview,
            question_id,
        )

        if attempt.status not in (
            QuestionAttemptStatus.PENDING,
            QuestionAttemptStatus.IN_PROGRESS,
        ):
            raise InvalidStateTransitionError(
                f"Question '{question_id}' cannot be skipped "
                f"from status '{attempt.status.value}'"
            )

        now = datetime.now(timezone.utc)
        started_at = attempt.question_started_at or now

        attempt.answered_at = now
        attempt.elapsed_seconds = max(
            0,
            int((now - started_at).total_seconds()),
        )
        attempt.status = QuestionAttemptStatus.SKIPPED

        self._advance_to_next_pending(interview)

        await self._interviews.update(interview)

        return self._to_attempt_response(attempt)

    def _advance_to_next_pending(
        self,
        interview: InterviewSession,
    ) -> None:
        for idx in range(
            interview.current_question_index + 1,
            len(interview.questions),
        ):
            interview.current_question_index = idx
            next_attempt = interview.questions[idx]

            if next_attempt.status == QuestionAttemptStatus.PENDING:
                next_attempt.status = QuestionAttemptStatus.IN_PROGRESS
                next_attempt.question_started_at = datetime.now(
                    timezone.utc
                )

            return

        # No more questions; keep index at the last one.
        interview.current_question_index = max(
            0,
            len(interview.questions) - 1,
        )

    async def complete_interview(
        self,
        session_id: str,
        user_id: str,
    ) -> InterviewDetailResponse:
        interview = await self._get_owned_interview(
            session_id,
            user_id,
        )

        if interview.status != InterviewStatus.IN_PROGRESS:
            raise InvalidStateTransitionError(
                f"Cannot complete an interview in status "
                f"'{interview.status.value}'"
            )

        now = datetime.now(timezone.utc)

        interview.status = InterviewStatus.COMPLETED
        interview.completed_at = now

        qa_payload = [
            {
                "question_id": q.question_id,
                "text": q.text,
                "status": q.status.value,
                "answer_text": q.answer_text,
            }
            for q in interview.questions
        ]

        feedback_data = await self._llm.generate_feedback(
            job_title=interview.profile_snapshot.job_title or "",
            questions_and_answers=qa_payload,
        )

        interview.feedback = FeedbackReport(
            summary=feedback_data["summary"],
            overall_score=feedback_data["overall_score"],
            strengths=feedback_data.get("strengths", []),
            improvements=feedback_data.get("improvements", []),
            per_question_feedback=feedback_data.get(
                "per_question_feedback",
                [],
            ),
            generated_at=now,
        )

        updated = await self._interviews.update(interview)

        return self._to_detail_response(updated)

    async def get_feedback(
        self,
        session_id: str,
        user_id: str,
    ) -> FeedbackResponse:
        interview = await self._get_owned_interview(
            session_id,
            user_id,
        )

        if interview.feedback is None:
            raise NotFoundError(
                "Feedback has not been generated for this interview yet"
            )

        return FeedbackResponse(
            summary=interview.feedback.summary,
            overall_score=interview.feedback.overall_score,
            strengths=interview.feedback.strengths,
            improvements=interview.feedback.improvements,
            per_question_feedback=(
                interview.feedback.per_question_feedback
            ),
            generated_at=interview.feedback.generated_at,
        )

    # --- Helpers ---------------------------------------------------------

    async def _get_owned_interview(
        self,
        session_id: str,
        user_id: str,
    ) -> InterviewSession:
        interview = await self._interviews.get_by_id(session_id)

        if interview is None:
            raise NotFoundError(
                f"Interview session {session_id} not found"
            )

        interview.ensure_owner(user_id)

        return interview

    @staticmethod
    def _ensure_in_progress(
        interview: InterviewSession,
    ) -> None:
        if interview.status != InterviewStatus.IN_PROGRESS:
            raise InvalidStateTransitionError(
                f"Interview must be in progress "
                f"(current status: '{interview.status.value}')"
            )

    @staticmethod
    def _get_question_or_404(
        interview: InterviewSession,
        question_id: str,
    ) -> QuestionAttempt:
        attempt = interview.find_question(question_id)

        if attempt is None:
            raise NotFoundError(
                f"Question {question_id} does not belong to "
                f"interview {interview.id}"
            )

        return attempt

    def _remaining_seconds(
        self,
        attempt: QuestionAttempt,
    ) -> Optional[int]:
        if (
            attempt.status != QuestionAttemptStatus.IN_PROGRESS
            or attempt.question_started_at is None
        ):
            return None

        elapsed = (
            datetime.now(timezone.utc)
            - attempt.question_started_at
        ).total_seconds()

        return max(
            0,
            int(attempt.time_limit_seconds - elapsed),
        )

    def _to_attempt_response(
        self,
        attempt: QuestionAttempt,
    ) -> QuestionAttemptResponse:
        return QuestionAttemptResponse(
            question_id=attempt.question_id,
            order=attempt.order,
            text=attempt.text,
            category=attempt.category,
            source=attempt.source,
            time_limit_seconds=attempt.time_limit_seconds,
            status=attempt.status,
            question_started_at=attempt.question_started_at,
            answered_at=attempt.answered_at,
            answer_text=attempt.answer_text,
            elapsed_seconds=attempt.elapsed_seconds,
            remaining_seconds=self._remaining_seconds(attempt),
        )

    def _to_detail_response(
        self,
        interview: InterviewSession,
    ) -> InterviewDetailResponse:
        return InterviewDetailResponse(
            id=interview.id,
            user_id=interview.user_id,
            title=interview.title,
            status=interview.status,
            profile_snapshot=ProfileSnapshotResponse(
                job_posting_id=(
                    interview.profile_snapshot.job_posting_id
                ),
                cv_id=interview.profile_snapshot.cv_id,
                job_title=interview.profile_snapshot.job_title,
                job_description=(
                    interview.profile_snapshot.job_description
                ),
                cv_summary=interview.profile_snapshot.cv_summary,
            ),
            questions=[
                self._to_attempt_response(q)
                for q in interview.questions
            ],
            current_question_index=(
                interview.current_question_index
            ),
            feedback=(
                FeedbackResponse(
                    summary=interview.feedback.summary,
                    overall_score=interview.feedback.overall_score,
                    strengths=interview.feedback.strengths,
                    improvements=interview.feedback.improvements,
                    per_question_feedback=(
                        interview.feedback.per_question_feedback
                    ),
                    generated_at=interview.feedback.generated_at,
                )
                if interview.feedback
                else None
            ),
            created_at=interview.created_at,
            started_at=interview.started_at,
            completed_at=interview.completed_at,
        )

    def _to_summary_response(
        self,
        interview: InterviewSession,
    ) -> InterviewSummaryResponse:
        return InterviewSummaryResponse(
            id=interview.id,
            title=interview.title,
            status=interview.status,
            total_questions=len(interview.questions),
            overall_score=(
                interview.feedback.overall_score
                if interview.feedback
                else None
            ),
            created_at=interview.created_at,
            started_at=interview.started_at,
            completed_at=interview.completed_at,
        )