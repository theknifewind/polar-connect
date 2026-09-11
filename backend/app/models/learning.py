"""LearningTopic and QuizQuestion ORM models."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class LearningTopic(Base):
    __tablename__ = "learning_topics"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    tag = Column(String)                       # "Start here", "Compare", "Explore", …
    description = Column(Text)
    color = Column(String, default="cyan")     # Gradient color key
    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship(
        "QuizQuestion", back_populates="topic", cascade="all, delete-orphan"
    )


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(String, primary_key=True)
    topic_id = Column(
        String,
        ForeignKey("learning_topics.id", ondelete="CASCADE"),
        nullable=False,
    )
    question = Column(String, nullable=False)
    options = Column(JSON, nullable=False)          # ["A", "B", "C", "D"]
    correct_answer_index = Column(Integer, nullable=False)
    explanation = Column(Text)
    sort_order = Column(Integer, default=0)

    topic = relationship("LearningTopic", back_populates="questions")
