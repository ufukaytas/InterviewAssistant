"""MongoDB implementation of the InterviewRepository interface."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

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

COLLECTION_NAME = "interviews"


def _attempt_to_doc(attempt: QuestionAttempt) -> dict[str, Any]:
    return {
        "question_id": attempt.question_id,
        "order": attempt.order,
        "text": attempt.text,
        "category": attempt.category,
        "source": attempt.source.value,
        "time_limit_seconds": attempt.time_limit_seconds,
        "status": attempt.status.value,
        "question_started_at": attempt.question_started_at,
        "answered_at": attempt.answered_at,
        "answer_text": attempt.answer_text,
        "elapsed_seconds": attempt.elapsed_seconds,
    }


def _attempt_from_doc(doc: dict[str, Any]) -> QuestionAttempt:
    return QuestionAttempt(
        question_id=doc["question_id"],
        order=doc["order"],
        text=doc["text"],
        category=doc["category"],
        source=QuestionSource(doc["source"]),
        time_limit_seconds=doc["time_limit_seconds"],
        status=QuestionAttemptStatus(doc.get("status", QuestionAttemptStatus.PENDING.value)),
        question_started_at=doc.get("question_started_at"),
        answered_at=doc.get("answered_at"),
        answer_text=doc.get("answer_text"),
        elapsed_seconds=doc.get("elapsed_seconds"),
    )


def _snapshot_to_doc(snapshot: ProfileSnapshot) -> dict[str, Any]:
    return {
        "job_posting_id": snapshot.job_posting_id,
        "cv_id": snapshot.cv_id,
        "job_title": snapshot.job_title,
        "job_description": snapshot.job_description,
        "cv_summary": snapshot.cv_summary,
        "raw_job_posting": snapshot.raw_job_posting,
        "raw_cv": snapshot.raw_cv,
    }


def _snapshot_from_doc(doc: dict[str, Any]) -> ProfileSnapshot:
    return ProfileSnapshot(
        job_posting_id=doc.get("job_posting_id"),
        cv_id=doc.get("cv_id"),
        job_title=doc.get("job_title"),
        job_description=doc.get("job_description"),
        cv_summary=doc.get("cv_summary"),
        raw_job_posting=doc.get("raw_job_posting", {}),
        raw_cv=doc.get("raw_cv", {}),
    )


def _feedback_to_doc(feedback: Optional[FeedbackReport]) -> Optional[dict[str, Any]]:
    if feedback is None:
        return None
    return {
        "summary": feedback.summary,
        "overall_score": feedback.overall_score,
        "strengths": feedback.strengths,
        "improvements": feedback.improvements,
        "per_question_feedback": feedback.per_question_feedback,
        "generated_at": feedback.generated_at,
    }


def _feedback_from_doc(doc: Optional[dict[str, Any]]) -> Optional[FeedbackReport]:
    if not doc:
        return None
    return FeedbackReport(
        summary=doc["summary"],
        overall_score=doc["overall_score"],
        strengths=doc.get("strengths", []),
        improvements=doc.get("improvements", []),
        per_question_feedback=doc.get("per_question_feedback", []),
        generated_at=doc.get("generated_at"),
    )


def _to_document(interview: InterviewSession) -> dict[str, Any]:
    return {
        "_id": interview.id,
        "user_id": interview.user_id,
        "title": interview.title,
        "status": interview.status.value,
        "profile_snapshot": _snapshot_to_doc(interview.profile_snapshot),
        "questions": [_attempt_to_doc(q) for q in interview.questions],
        "current_question_index": interview.current_question_index,
        "feedback": _feedback_to_doc(interview.feedback),
        "created_at": interview.created_at,
        "started_at": interview.started_at,
        "completed_at": interview.completed_at,
        "updated_at": interview.updated_at,
    }


def _from_document(doc: dict[str, Any]) -> InterviewSession:
    return InterviewSession(
        id=doc["_id"],
        user_id=doc["user_id"],
        title=doc["title"],
        status=InterviewStatus(doc["status"]),
        profile_snapshot=_snapshot_from_doc(doc.get("profile_snapshot", {})),
        questions=[_attempt_from_doc(q) for q in doc.get("questions", [])],
        current_question_index=doc.get("current_question_index", 0),
        feedback=_feedback_from_doc(doc.get("feedback")),
        created_at=doc.get("created_at"),
        started_at=doc.get("started_at"),
        completed_at=doc.get("completed_at"),
        updated_at=doc.get("updated_at"),
    )


class MongoInterviewRepository(InterviewRepository):
    def __init__(self, database: AsyncIOMotorDatabase):
        self._collection = database[COLLECTION_NAME]

    async def create(self, interview: InterviewSession) -> InterviewSession:
        if not interview.id:
            interview.id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        interview.created_at = interview.created_at or now
        interview.updated_at = now
        await self._collection.insert_one(_to_document(interview))
        return interview

    async def get_by_id(self, session_id: str) -> Optional[InterviewSession]:
        doc = await self._collection.find_one({"_id": session_id})
        return _from_document(doc) if doc else None

    async def list_for_user(
        self,
        user_id: str,
        *,
        status: Optional[InterviewStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[InterviewSession], int]:
        query: dict[str, Any] = {"user_id": user_id}
        if status:
            query["status"] = status.value

        total = await self._collection.count_documents(query)
        cursor = (
            self._collection.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [_from_document(d) for d in docs], total

    async def update(self, interview: InterviewSession) -> InterviewSession:
        interview.updated_at = datetime.now(timezone.utc)
        await self._collection.replace_one({"_id": interview.id}, _to_document(interview))
        return interview

    async def delete(self, session_id: str) -> bool:
        result = await self._collection.delete_one({"_id": session_id})
        return result.deleted_count > 0
