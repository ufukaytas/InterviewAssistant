"""LLM layer used for generated questions and feedback synthesis.

`LLMClient` is the interface the application services depend on. Two
implementations exist:

- `HttpLLMClient`: calls a real provider over HTTP. The API key is read ONLY
  from the environment (`LLM_API_KEY`) and is never logged or hard-coded.
- `StubLLMClient`: deterministic offline stand-in, used automatically when no
  `LLM_API_KEY` is configured (local development and unit tests).

`build_llm_client(settings)` picks the right one.
"""
from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.core.config import Settings
from app.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    @abstractmethod
    async def generate_questions(
        self, *, job_title: str, job_description: str, cv_summary: str, count: int
    ) -> list[dict[str, Any]]:
        """Return a list of {text, category, difficulty} dicts."""
        ...

    @abstractmethod
    async def generate_feedback(
        self,
        *,
        job_title: str,
        questions_and_answers: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Return a feedback dict: summary, overall_score, strengths, improvements,
        per_question_feedback."""
        ...


class StubLLMClient(LLMClient):
    """Deterministic, offline stand-in for a real LLM provider."""

    async def generate_questions(
        self, *, job_title: str, job_description: str, cv_summary: str, count: int
    ) -> list[dict[str, Any]]:
        role = job_title or "this role"
        base_questions = [
            f"Tell me about a project relevant to {role} that you are proud of.",
            f"What challenges do you expect in a {role} position, and how would you address them?",
            "Describe a time you disagreed with a teammate. How did you resolve it?",
            "Walk me through how you would debug a production issue under time pressure.",
            "What is a technical decision you made that you would reconsider today?",
            "How do you prioritize tasks when everything seems urgent?",
        ]
        selected = (base_questions * ((count // len(base_questions)) + 1))[:count]
        return [
            {"text": text, "category": "general", "difficulty": "medium"}
            for text in selected
        ]

    async def generate_feedback(
        self,
        *,
        job_title: str,
        questions_and_answers: list[dict[str, Any]],
    ) -> dict[str, Any]:
        answered = [qa for qa in questions_and_answers if qa.get("answer_text")]
        skipped = [qa for qa in questions_and_answers if qa.get("status") == "skipped"]
        total = len(questions_and_answers) or 1
        score = round(100 * len(answered) / total, 2)

        per_question = [
            {
                "question_id": qa.get("question_id"),
                "text": qa.get("text"),
                "status": qa.get("status"),
                "comment": (
                    "Answered within the allotted time."
                    if qa.get("status") == "answered"
                    else "This question was skipped."
                ),
            }
            for qa in questions_and_answers
        ]

        return {
            "summary": (
                f"You answered {len(answered)} of {len(questions_and_answers)} questions "
                f"for the {job_title or 'target'} interview."
            ),
            "overall_score": score,
            "strengths": ["Consistent engagement with the questions asked."] if answered else [],
            "improvements": ["Try to attempt every question, even partially."] if skipped else [],
            "per_question_feedback": per_question,
        }


# --- Real provider ----------------------------------------------------------

_DEFAULT_BASE_URLS = {
    "anthropic": "https://api.anthropic.com",
    "openai": "https://api.openai.com/v1",
}
_DEFAULT_MODELS = {"anthropic": "claude-sonnet-5", "openai": "gpt-4o-mini"}
# azure_openai has no sensible default: LLM_BASE_URL (the resource endpoint)
# and AZURE_OPENAI_DEPLOYMENT are both required for it.

_QUESTIONS_SYSTEM_PROMPT = (
    "You are an expert technical interviewer. Reply with JSON only, no prose and "
    "no markdown fences. Write in the same language as the job posting."
)
_FEEDBACK_SYSTEM_PROMPT = (
    "You are an expert interview coach. Reply with JSON only, no prose and no "
    "markdown fences. Write in the same language as the questions."
)


def _extract_json(text: str) -> Any:
    """Parse JSON from a model reply, tolerating accidental ```json fences."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ExternalServiceError(
            "The LLM returned a response that was not valid JSON", service="llm"
        ) from exc


class HttpLLMClient(LLMClient):
    """LLM client backed by an HTTP API (Anthropic, OpenAI-compatible, or Azure OpenAI)."""

    def __init__(self, settings: Settings) -> None:
        if settings.LLM_API_KEY is None:
            raise ValueError("LLM_API_KEY is required for HttpLLMClient")
        self._provider = settings.LLM_PROVIDER
        self._api_key = settings.LLM_API_KEY.get_secret_value()
        self._timeout = settings.LLM_TIMEOUT_SECONDS
        self._max_tokens = settings.LLM_MAX_TOKENS

        if self._provider == "azure_openai":
            if not settings.LLM_BASE_URL or not settings.AZURE_OPENAI_DEPLOYMENT:
                raise ValueError(
                    "LLM_BASE_URL (resource endpoint) and AZURE_OPENAI_DEPLOYMENT "
                    "are both required when LLM_PROVIDER=azure_openai"
                )
            self._model = settings.AZURE_OPENAI_DEPLOYMENT  # unused in the request body
            self._base_url = settings.LLM_BASE_URL.rstrip("/")
            self._api_version = settings.AZURE_OPENAI_API_VERSION
        else:
            self._model = settings.LLM_MODEL or _DEFAULT_MODELS[self._provider]
            self._base_url = (settings.LLM_BASE_URL or _DEFAULT_BASE_URLS[self._provider]).rstrip("/")

    async def generate_questions(
        self, *, job_title: str, job_description: str, cv_summary: str, count: int
    ) -> list[dict[str, Any]]:
        prompt = (
            f"Create {count} interview questions tailored to this candidate.\n"
            f"Job title: {job_title}\nJob description: {job_description}\n"
            f"Candidate CV summary: {cv_summary}\n\n"
            'Return a JSON array of objects: [{"text": str, "category": str, '
            '"difficulty": "easy"|"medium"|"hard"}].'
        )
        data = _extract_json(await self._complete(_QUESTIONS_SYSTEM_PROMPT, prompt))
        if not isinstance(data, list):
            raise ExternalServiceError("The LLM returned an unexpected question format", service="llm")

        questions = [
            {
                "text": str(item["text"]).strip(),
                "category": str(item.get("category") or "general"),
                "difficulty": str(item.get("difficulty") or "medium"),
            }
            for item in data
            if isinstance(item, dict) and str(item.get("text", "")).strip()
        ][:count]
        if not questions:
            raise ExternalServiceError("The LLM returned no usable questions", service="llm")
        return questions

    async def generate_feedback(
        self, *, job_title: str, questions_and_answers: list[dict[str, Any]]
    ) -> dict[str, Any]:
        prompt = (
            f"Evaluate this mock interview for the role: {job_title}.\n"
            f"Questions and answers (JSON): {json.dumps(questions_and_answers, ensure_ascii=False)}\n\n"
            'Return one JSON object: {"summary": str, "overall_score": number 0-100, '
            '"strengths": [str], "improvements": [str], "per_question_feedback": '
            '[{"question_id": str, "comment": str}]}. Skipped questions have no answer.'
        )
        data = _extract_json(await self._complete(_FEEDBACK_SYSTEM_PROMPT, prompt))
        if not isinstance(data, dict) or "summary" not in data:
            raise ExternalServiceError("The LLM returned an unexpected feedback format", service="llm")

        try:
            score = float(data.get("overall_score", 0))
        except (TypeError, ValueError):
            score = 0.0
        return {
            "summary": str(data["summary"]),
            "overall_score": max(0.0, min(100.0, score)),
            "strengths": [str(x) for x in data.get("strengths", [])],
            "improvements": [str(x) for x in data.get("improvements", [])],
            "per_question_feedback": data.get("per_question_feedback", []),
        }

    async def _complete(self, system_prompt: str, user_prompt: str) -> str:
        """Send one prompt to the provider and return the reply text."""
        if self._provider == "anthropic":
            url = f"{self._base_url}/v1/messages"
            headers = {"x-api-key": self._api_key, "anthropic-version": "2023-06-01"}
            body = {
                "model": self._model,
                "max_tokens": self._max_tokens,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
            }
        elif self._provider == "azure_openai":
            # Azure identifies the model via the deployment name in the URL
            # and authenticates with an "api-key" header, not Bearer auth.
            url = (
                f"{self._base_url}/openai/deployments/{self._model}/chat/completions"
                f"?api-version={self._api_version}"
            )
            headers = {"api-key": self._api_key}
            body = {
                "max_tokens": self._max_tokens,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            }
        else:  # openai-compatible
            url = f"{self._base_url}/chat/completions"
            headers = {"Authorization": f"Bearer {self._api_key}"}
            body = {
                "model": self._model,
                "max_tokens": self._max_tokens,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, headers=headers, json=body)
        except httpx.HTTPError as exc:
            # Log only the exception type: never headers, which contain the API key.
            logger.warning("LLM request failed (%s)", type(exc).__name__)
            raise ExternalServiceError("Could not reach the LLM provider", service="llm") from exc

        if response.status_code >= 400:
            logger.warning("LLM provider returned status %s", response.status_code)
            raise ExternalServiceError(
                "The LLM provider returned an error",
                service="llm",
                status_code=response.status_code,
            )

        try:
            payload = response.json()
            if self._provider == "anthropic":
                return "".join(b["text"] for b in payload["content"] if b.get("type") == "text")
            # azure_openai and openai both return the OpenAI chat-completions shape.
            return payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ExternalServiceError("Unexpected response from the LLM provider", service="llm") from exc


def build_llm_client(settings: Settings) -> LLMClient:
    """Use the real provider when LLM_API_KEY is set, otherwise the offline stub."""
    if settings.LLM_API_KEY is None or not settings.LLM_API_KEY.get_secret_value():
        logger.info("LLM_API_KEY not set: using the offline StubLLMClient")
        return StubLLMClient()
    return HttpLLMClient(settings)