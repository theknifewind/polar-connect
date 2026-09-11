"""Repository request/response DTOs matching the frontend RepositoryItem shape."""

from __future__ import annotations

from pydantic import BaseModel


class RepositoryItemResponse(BaseModel):
    id: str
    type: str
    title: str
    summary: str | None = None
    year: int | None = None
    region: str | None = None
    topics: list[str] = []
    meta: str | None = None
    accent: str | None = None
    icon: str | None = None
    file_url: str | None = None
    index_status: str | None = None
    created_at: str | None = None

    model_config = {"from_attributes": True}


class RepositoryItemCreate(BaseModel):
    id: str | None = None
    type: str
    title: str
    summary: str | None = None
    year: int | None = None
    region: str | None = None
    topics: list[str] = []
    meta: str | None = None


class RepositoryListResponse(BaseModel):
    items: list[RepositoryItemResponse]
    total: int
