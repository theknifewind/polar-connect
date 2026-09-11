"""Studio job creation, channel update and approval schemas."""

from __future__ import annotations

from pydantic import BaseModel


class StudioJobCreateRequest(BaseModel):
    repositoryItemId: str


class StudioChannelResponse(BaseModel):
    id: str
    channel: str
    label: str | None = None
    icon: str | None = None
    content: str | None = None
    approved: bool = False

    model_config = {"from_attributes": True}


class StudioJobResponse(BaseModel):
    id: str
    repositoryItemId: str
    status: str
    channels: list[StudioChannelResponse] = []
    createdAt: str | None = None


class StudioChannelUpdateRequest(BaseModel):
    channel: str
    editedContent: str | None = None
    approved: bool | None = None
