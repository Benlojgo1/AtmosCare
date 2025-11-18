from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv
import databases
import os

# Pydantic model for Location data (Simplified for example)
class LocationCreate(BaseModel):
    zip_code: str
    location_name: str
    population: int
    vulnerability_index: float

class LocationRow(LocationCreate):
    pass

@router.get("/locations", response_model=List[LocationRow])
async def get_all_locations():
    """Returns a list of all monitored locations."""
    query = "SELECT zip_code, location_name, population, vulnerability_index FROM location LIMIT 50"
    rows = await database.fetch_all(query)
    return [dict(row) for row in rows]

@router.post("/locations", status_code=201)
async def create_location(location: LocationCreate):
    """Adds a new location record (CREATE operation)."""
    query = """
        INSERT INTO location (zip_code, location_name, population, vulnerability_index)
        VALUES (:zip_code, :location_name, :population, :vulnerability_index)
    """
    values = location.dict()
    try:
        await database.execute(query=query, values=values)
        return {"message": f"Location {location.zip_code} created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Database error: {e}")

# Example: GET /api/locations