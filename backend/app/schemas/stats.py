"""Aggregate count response DTO for the homepage stats bar."""

from __future__ import annotations

from pydantic import BaseModel


class StatItem(BaseModel):
    value: str
    label: str


class StatsResponse(BaseModel):
    stats: list[StatItem]
