"""Abstract repository interface for the question pool (domain layer)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.question import Question
from app.domain.enums.interview_status import QuestionDifficulty, QuestionStatus


class QuestionRepository(ABC):
    @abstractmethod
    async def create(self, question: Question) -> Question:
        ...

    @abstractmethod
    async def get_by_id(self, question_id: str) -> Optional[Question]:
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    async def update(self, question: Question) -> Question:
        ...

    @abstractmethod
    async def archive(self, question_id: str) -> Optional[Question]:
        ...

    @abstractmethod
    async def list_random_pool(
        self,
        *,
        category: Optional[str] = None,
        difficulty: Optional[QuestionDifficulty] = None,
        count: int = 5,
    ) -> list[Question]:
        ...
