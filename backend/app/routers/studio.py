"""/api/studio — 6-channel draft generation, review & approval flow."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_admin
from app.database import get_db
from app.models.admin import AdminAccount
from app.models.studio import StudioChannelContent, StudioJob
from app.schemas.studio import (
    StudioChannelResponse,
    StudioChannelUpdateRequest,
    StudioJobCreateRequest,
    StudioJobResponse,
)
from app.services.studio_generator import generate_studio_job

router = APIRouter(prefix="/api/studio", tags=["studio"])


def _job_to_response(job: StudioJob) -> StudioJobResponse:
    return StudioJobResponse(
        id=job.id,
        repositoryItemId=job.repository_item_id,
        status=job.status,
        channels=[
            StudioChannelResponse(
                id=ch.id, channel=ch.channel, label=ch.label,
                icon=ch.icon, content=ch.content, approved=ch.approved,
            )
            for ch in job.channels
        ],
        createdAt=str(job.created_at) if job.created_at else None,
    )


# ── GET /api/studio/jobs ────────────────────────────────────

@router.get("/jobs", response_model=list[StudioJobResponse])
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(StudioJob).order_by(StudioJob.created_at.desc()).all()
    return [_job_to_response(j) for j in jobs]


# ── GET /api/studio/jobs/{id} ───────────────────────────────

@router.get("/jobs/{job_id}", response_model=StudioJobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(StudioJob).filter(StudioJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Studio job '{job_id}' not found")
    return _job_to_response(job)


# ── POST /api/studio/jobs (admin-only) ──────────────────────

@router.post("/jobs", response_model=StudioJobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    body: StudioJobCreateRequest,
    admin: AdminAccount = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    job = await generate_studio_job(body.repositoryItemId, db)
    return _job_to_response(job)


# ── PATCH /api/studio/jobs/{id} (admin-only) ────────────────

@router.patch("/jobs/{job_id}", response_model=StudioJobResponse)
def update_job(
    job_id: str,
    body: StudioChannelUpdateRequest,
    admin: AdminAccount = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    job = db.query(StudioJob).filter(StudioJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Studio job '{job_id}' not found")

    # Find the channel record
    channel_content = (
        db.query(StudioChannelContent)
        .filter(
            StudioChannelContent.job_id == job_id,
            StudioChannelContent.channel == body.channel,
        )
        .first()
    )
    if not channel_content:
        raise HTTPException(
            status_code=404,
            detail=f"Channel '{body.channel}' not found in job '{job_id}'",
        )

    # Apply edits
    if body.editedContent is not None:
        channel_content.content = body.editedContent
    if body.approved is not None:
        channel_content.approved = body.approved

    db.commit()

    # Auto-upgrade job status when all 6 channels are approved
    all_channels = (
        db.query(StudioChannelContent)
        .filter(StudioChannelContent.job_id == job_id)
        .all()
    )
    all_approved = all(ch.approved for ch in all_channels) and len(all_channels) == 6

    if all_approved:
        job.status = "Approved"
    elif any(ch.approved for ch in all_channels):
        job.status = "Review"

    db.commit()
    db.refresh(job)
    return _job_to_response(job)
