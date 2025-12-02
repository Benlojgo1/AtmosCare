from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

# import the shared async Database instance
from utils.database import database

router = APIRouter()  # main.py will mount this at prefix="/api"


# ----- Pydantic models -----

class LocationCreate(BaseModel):
    zip_code: str
    location_name: str
    population: int
    vulnerability_index: float


class LocationRow(LocationCreate):
    """Represents a row returned from the LOCATION table."""
    pass


# ----- Routes -----


@router.get("/locations", response_model=List[LocationRow])
async def get_all_locations():
    """
    Returns a list of all monitored locations.
    GET /api/locations
    """
    query = """
        SELECT zip_code,
                location_name,
                population,
                vulnerability_index
        FROM location
        ORDER BY zip_code
        LIMIT 50;
    """
    rows = await database.fetch_all(query)
    # rows is a list of Mapping objects; Pydantic can consume dicts
    return [LocationRow(**dict(row)) for row in rows]


@router.get("/locations/{zip_code}", response_model=LocationRow)
async def get_location(zip_code: str):
    """
    Returns a single location by ZIP code.
    GET /api/locations/{zip_code}
    """
    query = """
        SELECT zip_code,
                location_name,
                population,
                vulnerability_index
        FROM location
        WHERE zip_code = :zip_code;
    """
    row = await database.fetch_one(query, values={"zip_code": zip_code})
    if row is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return LocationRow(**dict(row))


@router.post("/locations", response_model=LocationRow, status_code=201)
async def create_location(location: LocationCreate):
    """
    Adds a new location record (CREATE operation).
    POST /api/locations
    """
    insert_query = """
        INSERT INTO location (zip_code, location_name, population, vulnerability_index)
        VALUES (:zip_code, :location_name, :population, :vulnerability_index)
        RETURNING zip_code, location_name, population, vulnerability_index;
    """
    try:
        row = await database.fetch_one(insert_query, values=location.dict())
        return LocationRow(**dict(row))
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..schemas import LocationCreate, LocationUpdate, LocationRead  
from ..crud import locations as locations_crud

# Assumes backend/db.py defines get_db() -> yields Session
from ..db import get_db  

router = APIRouter(prefix="/api/locations", tags=["locations"])


@router.post("/", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
def create_location(payload: LocationCreate, db: Session = Depends(get_db)):
    """
    Create a location.
    """
    try:
        loc = locations_crud.create_location(db, payload)
    except Exception as e:
        
        raise HTTPException(status_code=500, detail="Failed to create location") from e
    return loc

@router.put("/locations/{zip_code}", response_model=LocationRow)
async def update_location(zip_code: str, location: LocationCreate):
    """
    Updates an existing location.
    PUT /api/locations/{zip_code}
    """
    update_query = """
        UPDATE location
        SET location_name = :location_name,
            population = :population,
            vulnerability_index = :vulnerability_index
        WHERE zip_code = :zip_code
        RETURNING zip_code, location_name, population, vulnerability_index;
    """
    values = {**location.dict(), "zip_code": zip_code}
    row = await database.fetch_one(update_query, values=values)

    if row is None:
        raise HTTPException(status_code=404, detail="Location not found")

    return LocationRow(**dict(row))


@router.delete("/locations/{zip_code}")
async def delete_location(zip_code: str):
    """
    Deletes a location by ZIP code.
    DELETE /api/locations/{zip_code}
    """
    delete_query = "DELETE FROM location WHERE zip_code = :zip_code;"
    result = await database.execute(delete_query, values={"zip_code": zip_code})

    # databases.execute returns the last inserted id for some drivers,
    # but for DELETE we just check whether anything was affected by doing a follow-up SELECT
    check_query = "SELECT 1 FROM location WHERE zip_code = :zip_code;"
    still_there = await database.fetch_one(check_query, values={"zip_code": zip_code})
    if still_there:
        raise HTTPException(status_code=400, detail="Failed to delete location")

    return {"message": f"Location {zip_code} deleted successfully"}

@router.get("/", response_model=List[LocationRead])
def list_locations(db: Session = Depends(get_db)):
    return locations_crud.get_locations(db)


@router.get("/{location_id}", response_model=LocationRead)
def get_location(location_id: int, db: Session = Depends(get_db)):
    loc = locations_crud.get_location(db, location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return loc


@router.put("/{location_id}", response_model=LocationRead)
def update_location(location_id: int, payload: LocationUpdate, db: Session = Depends(get_db)):
    loc = locations_crud.update_location(db, location_id, payload)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return loc


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(location_id: int, db: Session = Depends(get_db)):
    ok = locations_crud.delete_location(db, location_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Location not found")
    # FastAPI will return an empty body with 204
    return None
