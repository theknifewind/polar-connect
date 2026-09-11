"""/api/learning — topics, quizzes & server-side grading."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.learning import LearningTopic, QuizQuestion
from app.schemas.learning import (
    LearningTopicResponse,
    QuizQuestionResponse,
    QuizQuestionResult,
    QuizSubmitRequest,
    QuizSubmitResponse,
)

router = APIRouter(prefix="/api/learning", tags=["learning"])


# ── GET /api/learning/topics ─────────────────────────────────

@router.get("/topics", response_model=list[LearningTopicResponse])
def list_topics(db: Session = Depends(get_db)):
    topics = db.query(LearningTopic).all()
    return [
        LearningTopicResponse(
            id=t.id, title=t.title, tag=t.tag,
            description=t.description, progress=0, color=t.color,
        )
        for t in topics
    ]


# ── GET /api/learning/topics/{id} ────────────────────────────

@router.get("/topics/{topic_id}", response_model=LearningTopicResponse)
def get_topic(topic_id: str, db: Session = Depends(get_db)):
    topic = db.query(LearningTopic).filter(LearningTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic '{topic_id}' not found")
    return LearningTopicResponse(
        id=topic.id, title=topic.title, tag=topic.tag,
        description=topic.description, progress=0, color=topic.color,
    )


# ── GET /api/learning/topics/{id}/quiz ───────────────────────

@router.get("/topics/{topic_id}/quiz", response_model=list[QuizQuestionResponse])
def get_quiz(topic_id: str, db: Session = Depends(get_db)):
    """Return questions with correctAnswerIndex stripped (prevent cheating)."""
    topic = db.query(LearningTopic).filter(LearningTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic '{topic_id}' not found")

    questions = (
        db.query(QuizQuestion)
        .filter(QuizQuestion.topic_id == topic_id)
        .order_by(QuizQuestion.sort_order)
        .all()
    )
    return [QuizQuestionResponse(question=q.question, options=q.options) for q in questions]


# ── POST /api/learning/topics/{id}/quiz/submit ───────────────

@router.post("/topics/{topic_id}/quiz/submit", response_model=QuizSubmitResponse)
def submit_quiz(topic_id: str, body: QuizSubmitRequest, db: Session = Depends(get_db)):
    """Grade the quiz: compare answers server-side, return per-question results."""
    topic = db.query(LearningTopic).filter(LearningTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic '{topic_id}' not found")

    questions = (
        db.query(QuizQuestion)
        .filter(QuizQuestion.topic_id == topic_id)
        .order_by(QuizQuestion.sort_order)
        .all()
    )

    if len(body.answers) != len(questions):
        raise HTTPException(
            status_code=400,
            detail=f"Expected {len(questions)} answers, got {len(body.answers)}",
        )

    score = 0
    results: list[QuizQuestionResult] = []
    for i, q in enumerate(questions):
        selected = body.answers[i]
        is_correct = selected == q.correct_answer_index
        if is_correct:
            score += 1
        results.append(
            QuizQuestionResult(
                question=q.question,
                options=q.options,
                selectedAnswer=selected,
                correctAnswer=q.correct_answer_index,
                correct=is_correct,
                explanation=q.explanation,
            )
        )

    total = len(questions)
    return QuizSubmitResponse(
        score=score,
        total=total,
        percentage=round((score / total) * 100, 1) if total else 0,
        results=results,
    )
