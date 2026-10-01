"""Dependency providers for MongoDB-backed repositories."""
from __future__ import annotations

from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import ServiceUnavailableError
from app.domain.repositories.interview_repository import InterviewRepository
from app.domain.repositories.question_repository import QuestionRepository
from app.infrastructure.repositories.mongo_interview_repository import MongoInterviewRepository
from app.infrastructure.repositories.mongo_question_repository import MongoQuestionRepository


def get_database(request: Request) -> AsyncIOMotorDatabase:
    database = getattr(request.app.state, "mongodb", None)
    db = database.database if database is not None else None
    if db is None:
        raise ServiceUnavailableError("Database connection is not available")
    return db


def get_question_repository(request: Request) -> QuestionRepository:
    return MongoQuestionRepository(get_database(request))


def get_interview_repository(request: Request) -> InterviewRepository:
    return MongoInterviewRepository(get_database(request))
