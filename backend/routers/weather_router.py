from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..schemas import WeatherCreate, WeatherUpdate, WeatherRead  # adjust these names if needed
from ..crud import weather as weather_crud

# Assumes backend/db.py defines get_db() -> yields Session
from ..db import get_db  # <- change if your db dependency has a different name/location

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.post("/", response_model=WeatherRead, status_code=status.HTTP_201_CREATED)
def create_weather(payload: WeatherCreate, db: Session = Depends(get_db)):
    try:
        rec = weather_crud.create_weather_record(db, payload)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to create weather record")
    return rec


@router.get("/", response_model=List[WeatherRead])
def list_weather(db: Session = Depends(get_db)):
    return weather_crud.get_weather_records(db)


@router.get("/{weather_id}", response_model=WeatherRead)
def get_weather(weather_id: int, db: Session = Depends(get_db)):
    rec = weather_crud.get_weather_by_id(db, weather_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Weather record not found")
    return rec


@router.get("/by-location/{location_id}", response_model=List[WeatherRead])
def get_weather_for_location(location_id: int, db: Session = Depends(get_db)):
    return weather_crud.get_weather_by_location(db, location_id)


@router.put("/{weather_id}", response_model=WeatherRead)
def update_weather(weather_id: int, payload: WeatherUpdate, db: Session = Depends(get_db)):
    rec = weather_crud.update_weather_record(db, weather_id, payload)
    if not rec:
        raise HTTPException(status_code=404, detail="Weather record not found")
    return rec


@router.delete("/{weather_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_weather(weather_id: int, db: Session = Depends(get_db)):
    ok = weather_crud.delete_weather_record(db, weather_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Weather record not found")
    return None