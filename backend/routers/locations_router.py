from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv
import databases
import os

# --- 1. Load Environment Variables ---
load_dotenv() 

# --- 2. Construct DATABASE_URL from Components ---
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'atmoscare')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')

# Check if essential credentials exist; if so, construct the URL
if DB_USER and DB_PASSWORD and DB_NAME:
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    DATABASE_URL = "postgresql://postgres:password@localhost:5432/atmoscare" 
    
# --- 3. Initialize Async database connection ---
database = databases.Database(DATABASE_URL)

# Define the router instance
router = APIRouter()

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