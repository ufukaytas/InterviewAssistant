"""Pydantic schemas for the Question Pool API."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.domain.enums.interview_status import QuestionDifficulty, QuestionStatus


class QuestionCreateRequest(BaseModel):
    text: str = Field(min_length=3, max_length=2000)
    category: str = Field(min_length=1, max_length=100)
    difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM
    tags: list[str] = Field(default_factory=list)
    time_limit_seconds: int = Field(default=120, ge=10, le=3600)

    @field_validator("text")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("text must not be blank")
        return v.strip()


class QuestionUpdateRequest(BaseModel):
    text: Optional[str] = Field(default=None, min_length=3, max_length=2000)
    category: Optional[str] = Field(default=None, min_length=1, max_length=100)
    difficulty: Optional[QuestionDifficulty] = None
    tags: Optional[list[str]] = None
    time_limit_seconds: Optional[int] = Field(default=None, ge=10, le=3600)


class QuestionResponse(BaseModel):
    id: str
    text: str
    category: str
    difficulty: QuestionDifficulty
    tags: list[str]
    time_limit_seconds: int
    status: QuestionStatus
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
