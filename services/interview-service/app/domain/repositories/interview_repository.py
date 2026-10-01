"""Abstract repository interface for interview sessions (domain layer)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.interview import InterviewSession
from app.domain.enums.interview_status import InterviewStatus


class InterviewRepository(ABC):
    @abstractmethod
    async def create(self, interview: InterviewSession) -> InterviewSession:
        ...

    @abstractmethod
    async def get_by_id(self, session_id: str) -> Optional[InterviewSession]:
        ...

    @abstractmethod
    async def list_for_user(
        self,
        user_id: str,
        *,
        status: Optional[InterviewStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[InterviewSession], int]:
        ...

    @abstractmethod
    async def update(self, interview: InterviewSession) -> InterviewSession:
        ...

    @abstractmethod
    async def delete(self, session_id: str) -> bool:
        ...
