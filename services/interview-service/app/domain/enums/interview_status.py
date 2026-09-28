"""Enumerations describing interview and question lifecycle states."""
from enum import Enum


class InterviewStatus(str, Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class QuestionAttemptStatus(str, Enum):
    """Status of a single question within an interview session."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ANSWERED = "answered"
    SKIPPED = "skipped"


class QuestionSource(str, Enum):
    POOL = "pool"
    GENERATED = "generated"


class QuestionDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionStatus(str, Enum):
    """Lifecycle status of a question in the question pool."""

    ACTIVE = "active"
    ARCHIVED = "archived"
