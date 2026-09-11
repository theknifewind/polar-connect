"""Assistant query request, dual-mode answer & source citation DTOs."""

from __future__ import annotations

from pydantic import BaseModel


class AssistantQueryRequest(BaseModel):
    question: str
    simplified: bool = False


class SourceCitation(BaseModel):
    id: str
    title: str
    type: str


class AssistantQueryResponse(BaseModel):
    detailedAnswer: str
    simplifiedAnswer: str
    usedSourceIds: list[str]
    sources: list[SourceCitation]
