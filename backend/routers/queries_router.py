from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
import databases
import os
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
# NOTE: The database connection and Pydantic models must be accessible (as in the previous examples)
DATABASE_URL = os.getenv("DATABASE_URL")
database = databases.Database(DATABASE_URL)

# Pydantic models for the analytical results (assuming these are imported from models.py)
class CompareZipRow(BaseModel):
    ZipCode: str
    AvgTemp: float
    AvgHumidity: float

class HighRiskRow(BaseModel):
    ZipCode: str
    VulnerabilityIndex: float

@router.get("/queries/compare", response_model=List[CompareZipRow])
async def compare_zips(zip1: str = Query(...), zip2: str = Query(...)):
    """Query 5: Compares average temperature and humidity between two ZIP codes."""
    # (Insert the full analytical SQL query from the previous step here)
    query = """
        SELECT zip_code AS "ZipCode", AVG(temperature) AS "AvgTemp", AVG(humidity) AS "AvgHumidity"
        FROM weather_record
        WHERE zip_code IN (:zip1, :zip2)
        GROUP BY zip_code
    """
    rows = await database.fetch_all(query=query, values={"zip1": zip1, "zip2": zip2})
    return [dict(row) for row in rows]

@router.get("/queries/high-risk", response_model=List[HighRiskRow])
async def high_risk_locations(aqi: float = Query(100.0), vulnerability_threshold: float = Query(0.7)):
    """Query 1: Finds locations with high AQI AND high vulnerability."""
    # (Insert the full analytical SQL query from the previous step here)
    query = """
        SELECT L.zip_code AS "ZipCode", L.vulnerability_index AS "VulnerabilityIndex"
        FROM location L JOIN weather_record R ON L.zip_code = R.zip_code
        WHERE R.air_quality_index > :aqi AND L.vulnerability_index >= :vulnerability_threshold
        LIMIT 50
    """
    rows = await database.fetch_all(query=query, values={"aqi": aqi, "vulnerability_threshold": vulnerability_threshold})
    return [dict(row) for row in rows]

# Example: GET /api/queries/compare?zip1=90210&zip2=78520