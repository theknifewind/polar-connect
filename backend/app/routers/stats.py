"""/api/stats — live homepage aggregations."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.learning import LearningTopic
from app.models.media import MediaStory
from app.models.repository import RepositoryItem
from app.schemas.stats import StatItem, StatsResponse

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """Dynamic SQL count query matching the frontend stats bar."""
    expeditions = (
        db.query(RepositoryItem).filter(RepositoryItem.type == "Report").count()
    )
    publications = (
        db.query(RepositoryItem)
        .filter(RepositoryItem.type.in_(["Publication", "Dataset"]))
        .count()
    )
    media_assets = (
        db.query(MediaStory).count()
        + db.query(RepositoryItem)
        .filter(RepositoryItem.type.in_(["Photo", "Video", "News"]))
        .count()
    )
    learning_paths = db.query(LearningTopic).count()

    return StatsResponse(
        stats=[
            StatItem(value=str(expeditions), label="Expedition records"),
            StatItem(value=str(publications), label="Publications"),
            StatItem(value=str(media_assets), label="Media assets"),
            StatItem(value=str(learning_paths), label="Learning paths"),
        ]
    )
