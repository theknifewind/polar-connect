"""Learning topic, quiz question & evaluation schemas."""

from __future__ import annotations

from pydantic import BaseModel


class LearningTopicResponse(BaseModel):
    id: str
    title: str
    tag: str | None = None
    description: str | None = None
    progress: int = 0          # Always 0 from server; client tracks progress
    color: str | None = None

    model_config = {"from_attributes": True}


class QuizQuestionResponse(BaseModel):
    """Strips correctAnswerIndex to prevent client-side cheating."""
    question: str
    options: list[str]

    model_config = {"from_attributes": True}


class QuizSubmitRequest(BaseModel):
    answers: list[int]


class QuizQuestionResult(BaseModel):
    question: str
    options: list[str]
    selectedAnswer: int
    correctAnswer: int
    correct: bool
    explanation: str | None = None


class QuizSubmitResponse(BaseModel):
    score: int
    total: int
    percentage: float
    results: list[QuizQuestionResult]
