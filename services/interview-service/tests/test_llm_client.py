"""Tests for the LLM layer. No real provider is ever called: httpx is mocked."""
from __future__ import annotations

import json

import httpx
import pytest

import app.infrastructure.external_clients.llm_client as llm_module
from app.core.config import Settings
from app.core.exceptions import ExternalServiceError
from app.infrastructure.external_clients.llm_client import (
    HttpLLMClient,
    StubLLMClient,
    build_llm_client,
)

def _settings(**overrides) -> Settings:
    return Settings(_env_file=None, **overrides)


def _mock_httpx(monkeypatch, handler) -> None:
    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        llm_module.httpx,
        "AsyncClient",
        lambda **kw: real_client(transport=httpx.MockTransport(handler), **kw),
    )


def test_stub_is_used_when_no_api_key():
    assert isinstance(build_llm_client(_settings()), StubLLMClient)


def test_http_client_is_used_when_api_key_present():
    assert isinstance(build_llm_client(_settings(LLM_API_KEY="k")), HttpLLMClient)


def test_api_key_is_masked_in_settings_repr():
    assert "super-secret" not in repr(_settings(LLM_API_KEY="super-secret"))


async def test_anthropic_questions_parse_fenced_json(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/messages"
        assert request.headers["x-api-key"] == "test-key"
        reply = '```json\n[{"text": "Explain REST.", "category": "technical", "difficulty": "easy"}]\n```'
        return httpx.Response(200, json={"content": [{"type": "text", "text": reply}]})

    _mock_httpx(monkeypatch, handler)
    client = HttpLLMClient(_settings(LLM_API_KEY="test-key", LLM_PROVIDER="anthropic"))
    questions = await client.generate_questions(
        job_title="Dev", job_description="d", cv_summary="c", count=3
    )
    assert questions == [{"text": "Explain REST.", "category": "technical", "difficulty": "easy"}]


async def test_openai_feedback_is_normalized(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/chat/completions")
        assert request.headers["authorization"] == "Bearer test-key"
        reply = json.dumps({"summary": "Good", "overall_score": 250, "strengths": ["a"]})
        return httpx.Response(200, json={"choices": [{"message": {"content": reply}}]})

    _mock_httpx(monkeypatch, handler)
    client = HttpLLMClient(_settings(LLM_API_KEY="test-key", LLM_PROVIDER="openai"))
    feedback = await client.generate_feedback(job_title="Dev", questions_and_answers=[])
    assert feedback["overall_score"] == 100.0  # clamped to 0-100
    assert feedback["improvements"] == []


async def test_provider_error_becomes_external_service_error(monkeypatch):
    _mock_httpx(monkeypatch, lambda request: httpx.Response(401, json={"error": "bad key"}))
    client = HttpLLMClient(_settings(LLM_API_KEY="bad"))
    with pytest.raises(ExternalServiceError):
        await client.generate_questions(job_title="d", job_description="d", cv_summary="c", count=1)


async def test_invalid_json_becomes_external_service_error(monkeypatch):
    _mock_httpx(
        monkeypatch,
        lambda request: httpx.Response(200, json={"content": [{"type": "text", "text": "not json"}]}),
    )
    client = HttpLLMClient(_settings(LLM_API_KEY="k"))
    with pytest.raises(ExternalServiceError):
        await client.generate_questions(job_title="d", job_description="d", cv_summary="c", count=1)
