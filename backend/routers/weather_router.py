from typing import List
from pydantic import BaseModel
from datetime import datetime

from utils.database import database
from utils.api_fetcher import fetch_current_weather  
from anyio import to_thread
import os
API_KEY = os.getenv("WEATHER_API_KEY")
router = APIRouter()  # mounted in main.py with prefix="/api"


# ----- Pydantic models -----


class WeatherRecordRow(BaseModel):
    """Represents a row from the WEATHER_RECORD table."""
    record_id: int
    zip_code: str
    timestamp: datetime
    temperature: float
    humidity: float
    air_quality_index: int


class WeatherIngest(BaseModel):
    """Request body for ingesting fresh weather data via WeatherAPI."""
    zip_code: str


# ----- Routes -----


@router.get("/weather", response_model=List[WeatherRecordRow])
async def list_weather(
    zip: str = Query(..., description="ZIP code to filter WEATHER_RECORD by"),
    limit: int = Query(25, ge=1, le=500, description="Max number of records to return"),
):
    """
    Returns recent weather records for a given ZIP code from the database.
    GET /api/weather?zip=78224&limit=25
    """
    query = """
        SELECT record_id,
                zip_code,
                timestamp,
                temperature,
                humidity,
                air_quality_index
        FROM weather_record
        WHERE zip_code = :zip
        ORDER BY timestamp DESC
        LIMIT :limit;
    """

    rows = await database.fetch_all(query, values={"zip": zip, "limit": limit})
    if not rows:
        return []

    return [WeatherRecordRow(**dict(row)) for row in rows]


@router.post("/weather", response_model=WeatherRecordRow, status_code=201)
async def ingest_weather(body: WeatherIngest):
    """
    Calls WeatherAPI for the given ZIP and stores the result in WEATHER_RECORD.
    POST /api/weather
    Body: { "zip_code": "78224" }
    """
    zip_code = body.zip_code

    # 1) Fetch current conditions from external API
    try:
        data = await fetch_current_weather(zip_code)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch from WeatherAPI: {e}")

    if not data:
        raise HTTPException(status_code=404, detail=f"No weather data returned for ZIP {zip_code}")

    # 2) Insert into WEATHER_RECORD
    insert_query = """
        INSERT INTO weather_record (zip_code, timestamp, temperature, humidity, air_quality_index)
        VALUES (:zip_code, :timestamp, :temperature, :humidity, :air_quality_index)
        RETURNING record_id, zip_code, timestamp, temperature, humidity, air_quality_index;
    """

    values = {
        "zip_code": zip_code,
        "timestamp": data["timestamp"],
        "temperature": data["temperature"],
        "humidity": data["humidity"],
        "air_quality_index": data["air_quality_index"],
    }

    row = await database.fetch_one(insert_query, values=values)
    if row is None:
        raise HTTPException(status_code=500, detail="Failed to insert weather record into database")

    return WeatherRecordRow(**dict(row))

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..schemas import WeatherCreate, WeatherUpdate, WeatherRead 
from ..crud import weather as weather_crud


from ..db import get_db 

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
