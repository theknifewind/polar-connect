"""/api/media — stories, field notes, video metadata."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.media import MediaStory

router = APIRouter(prefix="/api/media", tags=["media"])


class MediaStoryResponse(BaseModel):
    id: str
    type: str | None = None
    eyebrow: str | None = None
    title: str
    summary: str | None = None
    gradient: str | None = None
    cover_url: str | None = None

    model_config = {"from_attributes": True}


@router.get("", response_model=list[MediaStoryResponse])
def list_media(type: str | None = None, db: Session = Depends(get_db)):
    query = db.query(MediaStory)
    if type and type != "All":
        query = query.filter(MediaStory.type == type)
    return [MediaStoryResponse.model_validate(s) for s in query.all()]


@router.get("/{story_id}", response_model=MediaStoryResponse)
def get_story(story_id: str, db: Session = Depends(get_db)):
    story = db.query(MediaStory).filter(MediaStory.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail=f"Media story '{story_id}' not found")
    return MediaStoryResponse.model_validate(story)
