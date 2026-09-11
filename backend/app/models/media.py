"""MediaStory ORM model — field notes, videos, photo essays, news."""

from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text

from app.database import Base


class MediaStory(Base):
    __tablename__ = "media_stories"

    id = Column(String, primary_key=True)
    type = Column(String)                     # "Field note" | "Video" | "Photo essay" | "News"
    eyebrow = Column(String)                  # "Antarctica · 08 min"
    title = Column(String, nullable=False)
    summary = Column(Text)
    gradient = Column(String, default="from-cyan-950 via-sky-900 to-slate-800")
    cover_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
