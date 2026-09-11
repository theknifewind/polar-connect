"""RepositoryItem ORM model — the core knowledge record."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text

from app.database import Base


class RepositoryItem(Base):
    __tablename__ = "repository_items"

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)          # Report | Publication | Dataset | Photo | Video | News | Learning
    title = Column(String, nullable=False)
    summary = Column(Text)
    year = Column(Integer)
    region = Column(String)                        # Antarctica | Arctic | Southern Ocean
    topics = Column(JSON, default=list)            # ["Expedition", "Climate change", …]
    meta = Column(String)                          # "PDF · 86 pages"
    accent = Column(String, default="from-cyan-300/30 via-sky-500/10 to-transparent")
    icon = Column(String, default="▱")
    file_url = Column(String)
    file_type = Column(String)
    raw_text = Column(Text)                        # Extracted full-text for RAG ingestion
    index_status = Column(String, default="pending")  # pending | indexed | failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
