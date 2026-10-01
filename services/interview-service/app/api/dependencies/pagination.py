"""Shared pagination query-parameter dependency."""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, Query

from app.api.dependencies.settings import get_app_settings
from app.core.config import Settings


@dataclass(frozen=True)
class PaginationParams:
    skip: int
    limit: int


def get_pagination_params(
    skip: int = Query(default=0, ge=0),
    limit: int | None = Query(default=None, ge=1),
    settings: Settings = Depends(get_app_settings),
) -> PaginationParams:
    effective_limit = limit or settings.DEFAULT_PAGE_SIZE
    effective_limit = min(effective_limit, settings.MAX_PAGE_SIZE)
    return PaginationParams(skip=skip, limit=effective_limit)
