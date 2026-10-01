"""Domain entity for a pooled interview question (framework-agnostic)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.domain.enums.interview_status import QuestionDifficulty, QuestionStatus


@dataclass
class Question:
    id: str
    text: str
    category: str
    difficulty: QuestionDifficulty
    tags: list[str] = field(default_factory=list)
    time_limit_seconds: int = 120
    status: QuestionStatus = QuestionStatus.ACTIVE
    created_by: Optional[str] = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def archive(self) -> None:
        self.status = QuestionStatus.ARCHIVED

    @property
    def is_active(self) -> bool:
        return self.status == QuestionStatus.ACTIVE
