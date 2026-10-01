"""Shared/reusable Pydantic schemas."""
from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    total: int
    skip: int
    limit: int


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    pagination: PaginationMeta


class ErrorResponse(BaseModel):
    error_code: str = Field(examples=["not_found"])
    message: str
    details: dict | None = None
