from typing import List
from pydantic import BaseModel
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException
import os

from backend.utils.database import database
from backend.utils.api_fetcher import fetch_current_weather

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
    if not API_KEY:
        raise HTTPException(status_code=500, detail="WEATHER_API_KEY not configured")

    try:
        # fetch_current_weather is a sync function, but we're in an async route
        # We need to use a thread pool to call the sync function
        from anyio import to_thread
        data = await to_thread.run_sync(fetch_current_weather, zip_code, API_KEY)
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
