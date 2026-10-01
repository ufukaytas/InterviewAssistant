"""Dependency providers that assemble application services with their
infrastructure collaborators (repositories, external clients)."""
from __future__ import annotations

from fastapi import Depends

from app.api.dependencies.database import get_interview_repository, get_question_repository
from app.api.dependencies.settings import get_app_settings
from app.application.services.interview_service import InterviewService
from app.application.services.question_service import QuestionService
from app.core.config import Settings
from app.domain.repositories.interview_repository import InterviewRepository
from app.domain.repositories.question_repository import QuestionRepository
from app.infrastructure.external_clients.llm_client import LLMClient, build_llm_client
from app.infrastructure.external_clients.profile_service_client import ProfileServiceClient


def get_profile_service_client(settings: Settings = Depends(get_app_settings)) -> ProfileServiceClient:
    return ProfileServiceClient(settings)


def get_llm_client(settings: Settings = Depends(get_app_settings)) -> LLMClient:
    return build_llm_client(settings)


def get_question_service(
    question_repository: QuestionRepository = Depends(get_question_repository),
) -> QuestionService:
    return QuestionService(question_repository)


def get_interview_service(
    interview_repository: InterviewRepository = Depends(get_interview_repository),
    question_repository: QuestionRepository = Depends(get_question_repository),
    profile_client: ProfileServiceClient = Depends(get_profile_service_client),
    llm_client: LLMClient = Depends(get_llm_client),
    settings: Settings = Depends(get_app_settings),
) -> InterviewService:
    return InterviewService(
        interview_repository=interview_repository,
        question_repository=question_repository,
        profile_client=profile_client,
        llm_client=llm_client,
        settings=settings,
    )
