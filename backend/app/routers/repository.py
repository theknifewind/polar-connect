"""/api/repository — CRUD, metadata filters, file upload & ingestion trigger."""

from __future__ import annotations

import json as json_lib
import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.config import settings
from app.core.auth import get_current_admin
from app.database import get_db
from app.models.admin import AdminAccount
from app.models.repository import RepositoryItem
from app.schemas.repository import RepositoryItemResponse, RepositoryListResponse
from app.services import vector_store
from app.services.ingestion import extract_text_from_file, ingest_document

router = APIRouter(prefix="/api/repository", tags=["repository"])

# ── Defaults by content type (match frontend polaris.ts) ────
ICON_MAP: dict[str, str] = {
    "Report": "▱", "Publication": "✦", "Dataset": "⌁",
    "Photo": "▧", "Video": "▶", "News": "↗", "Learning": "◎",
}
ACCENT_MAP: dict[str, str] = {
    "Report":      "from-cyan-300/30 via-sky-500/10 to-transparent",
    "Publication": "from-indigo-300/30 via-violet-500/10 to-transparent",
    "Dataset":     "from-emerald-300/25 via-teal-500/10 to-transparent",
    "Photo":       "from-sky-300/30 via-blue-600/10 to-transparent",
    "Video":       "from-orange-300/25 via-amber-500/10 to-transparent",
    "News":        "from-pink-300/25 via-fuchsia-500/10 to-transparent",
    "Learning":    "from-yellow-200/30 via-cyan-500/10 to-transparent",
}


def _to_response(item: RepositoryItem) -> RepositoryItemResponse:
    return RepositoryItemResponse(
        id=item.id,
        type=item.type,
        title=item.title,
        summary=item.summary,
        year=item.year,
        region=item.region,
        topics=item.topics or [],
        meta=item.meta,
        accent=item.accent,
        icon=item.icon,
        file_url=item.file_url,
        index_status=item.index_status,
        created_at=str(item.created_at) if item.created_at else None,
    )


# ── GET /api/repository ─────────────────────────────────────

@router.get("", response_model=RepositoryListResponse)
def list_items(
    q: Optional[str] = None,
    type: Optional[str] = None,
    region: Optional[str] = None,
    year: Optional[int] = None,
    topics: Optional[str] = None,
    sort: str = "relevance",
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(RepositoryItem)

    # Text search across title + summary
    if q:
        term = f"%{q}%"
        query = query.filter(
            or_(
                RepositoryItem.title.ilike(term),
                RepositoryItem.summary.ilike(term),
            )
        )

    # Discrete filters
    if type and type != "All types":
        query = query.filter(RepositoryItem.type == type)
    if region and region != "All regions":
        query = query.filter(RepositoryItem.region == region)
    if year:
        query = query.filter(RepositoryItem.year == year)

    # Topic filtering (JSON array contains) — SQLite vs PostgreSQL
    if topics and topics != "All topics":
        if settings.DATABASE_URL.startswith("sqlite"):
            query = query.filter(RepositoryItem.topics.like(f'%"{topics}"%'))
        else:
            query = query.filter(RepositoryItem.topics.contains([topics]))

    total = query.count()

    # Sort
    if sort == "newest":
        query = query.order_by(RepositoryItem.year.desc())
    elif sort == "oldest":
        query = query.order_by(RepositoryItem.year.asc())
    else:
        query = query.order_by(RepositoryItem.id)

    items = query.offset(skip).limit(limit).all()
    return RepositoryListResponse(items=[_to_response(i) for i in items], total=total)


# ── GET /api/repository/{id} ────────────────────────────────

@router.get("/{item_id}", response_model=RepositoryItemResponse)
def get_item(item_id: str, db: Session = Depends(get_db)):
    item = db.query(RepositoryItem).filter(RepositoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Repository item '{item_id}' not found")
    return _to_response(item)


# ── POST /api/repository (admin-only, multipart) ────────────

@router.post("", response_model=RepositoryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    title: str = Form(...),
    type: str = Form(...),
    summary: str = Form(""),
    year: int = Form(None),
    region: str = Form(None),
    topics: str = Form("[]"),          # JSON array string or comma-separated
    meta: str = Form(""),
    file: UploadFile = File(None),
    admin: AdminAccount = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    item_id = str(uuid.uuid4())[:8]

    # Parse topics
    try:
        parsed_topics = json_lib.loads(topics) if topics else []
    except json_lib.JSONDecodeError:
        parsed_topics = [t.strip() for t in topics.split(",") if t.strip()]

    # Handle file upload
    file_url = None
    file_type = None
    raw_text = ""

    if file and file.filename:
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        ext = os.path.splitext(file.filename)[1]
        file_name = f"{item_id}{ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, file_name)

        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        file_url = f"/uploads/{file_name}"
        file_type = ext.lstrip(".")
        raw_text = extract_text_from_file(file_path)

        if not meta:
            size_mb = len(contents) / (1024 * 1024)
            meta = f"{file_type.upper()} · {size_mb:.1f} MB"

    item = RepositoryItem(
        id=item_id,
        type=type,
        title=title,
        summary=summary,
        year=year,
        region=region,
        topics=parsed_topics,
        meta=meta,
        accent=ACCENT_MAP.get(type, ACCENT_MAP["Report"]),
        icon=ICON_MAP.get(type, "▱"),
        file_url=file_url,
        file_type=file_type,
        raw_text=raw_text,
        index_status="pending",
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    # Trigger vector ingestion
    if raw_text:
        try:
            idx_status = ingest_document(
                doc_id=item.id,
                raw_text=raw_text,
                doc_type=type,
                region=region or "",
                year=year or 0,
            )
            item.index_status = idx_status
            db.commit()
        except Exception:
            item.index_status = "failed"
            db.commit()

    return _to_response(item)


# ── DELETE /api/repository/{id} (admin-only) ────────────────

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: str,
    admin: AdminAccount = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    item = db.query(RepositoryItem).filter(RepositoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Repository item '{item_id}' not found")

    # Delete local file
    if item.file_url:
        path = os.path.join(settings.UPLOAD_DIR, os.path.basename(item.file_url))
        if os.path.exists(path):
            os.remove(path)

    # Delete ChromaDB chunks
    vector_store.delete_doc_chunks(item_id)

    db.delete(item)
    db.commit()
