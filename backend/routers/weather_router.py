from fastapi import APIRouter, Query, HTTPException
from typing import List
from pydantic import BaseModel
import databases
import os
import datetime
from dotenv import load_dotenv

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

# NOTE: You would typically get the API_KEY from the environment here
API_KEY = os.getenv('WEATHER_API_KEY') 

# Pydantic model for Weather data
class WeatherRow(BaseModel):
    timestamp: datetime.datetime
    temperature: float
    air_quality_index: int

@router.get("/weather/{zip_code}", response_model=WeatherRow)
async def get_latest_weather(zip_code: str):
    """
    Fetches and returns the latest real-time weather data for a ZIP code.
    (This is an API-fetch endpoint, not a standard DB read)
    """
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API_KEY is not configured.")

    # NOTE: You need the actual fetch function imported and called here
    # Example: 
    # data = fetch_current_weather(zip_code, API_KEY) 
    
    # Placeholder response structure for testing:
    data = {
        "timestamp": datetime.datetime.now(),
        "temperature": 25.5,
        "air_quality_index": 55,
    }

    if not data:
        raise HTTPException(status_code=404, detail=f"Weather data not found for {zip_code}")
        
    return data

# Example: GET /api/weather/78520