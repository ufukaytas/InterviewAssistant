"""Pydantic schemas for the local development token endpoint."""
from __future__ import annotations

from pydantic import BaseModel, Field


class DevTokenRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=200)


class DevTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
