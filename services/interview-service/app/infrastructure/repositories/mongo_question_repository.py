"""MongoDB implementation of the QuestionRepository interface."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.entities.question import Question
from app.domain.enums.interview_status import QuestionDifficulty, QuestionStatus
from app.domain.repositories.question_repository import QuestionRepository

COLLECTION_NAME = "questions"


def _to_document(question: Question) -> dict[str, Any]:
    return {
        "_id": question.id,
        "text": question.text,
        "category": question.category,
        "difficulty": question.difficulty.value,
        "tags": question.tags,
        "time_limit_seconds": question.time_limit_seconds,
        "status": question.status.value,
        "created_by": question.created_by,
        "created_at": question.created_at,
        "updated_at": question.updated_at,
    }


def _from_document(doc: dict[str, Any]) -> Question:
    return Question(
        id=doc["_id"],
        text=doc["text"],
        category=doc["category"],
        difficulty=QuestionDifficulty(doc["difficulty"]),
        tags=doc.get("tags", []),
        time_limit_seconds=doc.get("time_limit_seconds", 120),
        status=QuestionStatus(doc.get("status", QuestionStatus.ACTIVE.value)),
        created_by=doc.get("created_by"),
        created_at=doc.get("created_at"),
        updated_at=doc.get("updated_at"),
    )


class MongoQuestionRepository(QuestionRepository):
    def __init__(self, database: AsyncIOMotorDatabase):
        self._collection = database[COLLECTION_NAME]

    async def create(self, question: Question) -> Question:
        if not question.id:
            question.id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        question.created_at = question.created_at or now
        question.updated_at = now
        await self._collection.insert_one(_to_document(question))
        return question

    async def get_by_id(self, question_id: str) -> Optional[Question]:
        doc = await self._collection.find_one({"_id": question_id})
        return _from_document(doc) if doc else None

    async def list(
        self,
        *,
        category: Optional[str] = None,
        difficulty: Optional[QuestionDifficulty] = None,
        status: Optional[QuestionStatus] = None,
        tag: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Question], int]:
        query: dict[str, Any] = {}
        if category:
            query["category"] = category
        if difficulty:
            query["difficulty"] = difficulty.value
        if status:
            query["status"] = status.value
        if tag:
            query["tags"] = tag

        total = await self._collection.count_documents(query)
        cursor = (
            self._collection.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [_from_document(d) for d in docs], total

    async def update(self, question: Question) -> Question:
        question.updated_at = datetime.now(timezone.utc)
        await self._collection.replace_one({"_id": question.id}, _to_document(question))
        return question

    async def archive(self, question_id: str) -> Optional[Question]:
        question = await self.get_by_id(question_id)
        if question is None:
            return None
        question.archive()
        return await self.update(question)

    async def list_random_pool(
        self,
        *,
        category: Optional[str] = None,
        difficulty: Optional[QuestionDifficulty] = None,
        count: int = 5,
    ) -> list[Question]:
        match: dict[str, Any] = {"status": QuestionStatus.ACTIVE.value}
        if category:
            match["category"] = category
        if difficulty:
            match["difficulty"] = difficulty.value

        pipeline = [{"$match": match}, {"$sample": {"size": count}}]
        docs = await self._collection.aggregate(pipeline).to_list(length=count)
        return [_from_document(d) for d in docs]
