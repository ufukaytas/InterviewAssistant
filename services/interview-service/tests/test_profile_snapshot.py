"""Unit tests for InterviewService._build_profile_snapshot."""
from __future__ import annotations

from typing import Any

from app.application.schemas.interview_schemas import InterviewCreateRequest
from app.application.services.interview_service import InterviewService
from app.core.config import Settings


class _FakeProfile:
    def __init__(self, description: str = "desc", summary: str = "cv summary") -> None:
        self.description, self.summary = description, summary
        self.latest_cv_calls = 0

    async def get_job_posting(self, job_posting_id: str, auth_token=None) -> dict[str, Any]:
        return {"id": job_posting_id, "title": "Dev", "description": self.description}

    async def get_cv(self, cv_id: str, auth_token=None) -> dict[str, Any]:
        return {"id": cv_id, "summary": self.summary}

    async def get_latest_cv(self, user_id: str, auth_token=None) -> dict[str, Any]:
        self.latest_cv_calls += 1
        return {"id": "latest", "summary": self.summary}


def _service(profile: _FakeProfile, **settings_kw) -> InterviewService:
    settings = Settings(_env_file=None, **settings_kw)
    return InterviewService(None, None, profile, None, settings)  # type: ignore[arg-type]


async def test_only_job_posting_id_still_fetches_latest_cv():
    profile = _FakeProfile()
    snap = await _service(profile)._build_profile_snapshot(
        InterviewCreateRequest(job_posting_id="jp-1"), "user-1", "tok"
    )
    assert profile.latest_cv_calls == 1
    assert snap.cv_summary == "cv summary"
    assert snap.job_description == "desc"


async def test_explicit_cv_id_does_not_fetch_latest_cv():
    profile = _FakeProfile()
    await _service(profile)._build_profile_snapshot(
        InterviewCreateRequest(job_posting_id="jp-1", cv_id="cv-9"), "user-1", "tok"
    )
    assert profile.latest_cv_calls == 0


async def test_latest_cv_failure_is_best_effort():
    class Failing(_FakeProfile):
        async def get_latest_cv(self, user_id, auth_token=None):
            raise RuntimeError("profile down")

    snap = await _service(Failing())._build_profile_snapshot(
        InterviewCreateRequest(job_posting_id="jp-1"), "user-1", "tok"
    )
    assert snap.cv_summary is None and snap.job_description == "desc"


async def test_long_profile_texts_are_truncated():
    profile = _FakeProfile(description="x" * 50_000, summary="y" * 50_000)
    snap = await _service(profile, PROFILE_TEXT_MAX_CHARS=1000)._build_profile_snapshot(
        InterviewCreateRequest(job_posting_id="jp-1", cv_id="cv-1"), "user-1", "tok"
    )
    assert len(snap.job_description) == 1000
    assert len(snap.cv_summary) == 1000
