"""StudioJob and StudioChannelContent ORM models — outreach content generation."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class StudioJob(Base):
    __tablename__ = "studio_jobs"

    id = Column(String, primary_key=True)
    repository_item_id = Column(
        String, ForeignKey("repository_items.id"), nullable=False
    )
    status = Column(String, default="Drafted")  # Drafted | Review | Approved
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    channels = relationship(
        "StudioChannelContent", back_populates="job", cascade="all, delete-orphan"
    )
    repository_item = relationship("RepositoryItem")


class StudioChannelContent(Base):
    __tablename__ = "studio_channel_content"

    id = Column(String, primary_key=True)
    job_id = Column(
        String,
        ForeignKey("studio_jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    channel = Column(String, nullable=False)   # web | linkedin | instagram | x | education | newsletter
    label = Column(String)                     # Human-readable label
    icon = Column(String)                      # Unicode icon
    content = Column(Text)
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    job = relationship("StudioJob", back_populates="channels")
