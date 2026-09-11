"""/api/stations — static station geo & metadata."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.station import Station

router = APIRouter(prefix="/api/stations", tags=["stations"])


class StationResponse(BaseModel):
    id: str
    name: str
    region: str | None = None
    description: str | None = None
    established: str | None = None
    number: str | None = None
    facts: list[str] = []
    color: str | None = None
    map_x: str | None = None
    map_y: str | None = None

    model_config = {"from_attributes": True}


@router.get("", response_model=list[StationResponse])
def list_stations(db: Session = Depends(get_db)):
    return [StationResponse.model_validate(s) for s in db.query(Station).all()]


@router.get("/{station_id}", response_model=StationResponse)
def get_station(station_id: str, db: Session = Depends(get_db)):
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail=f"Station '{station_id}' not found")
    return StationResponse.model_validate(station)
