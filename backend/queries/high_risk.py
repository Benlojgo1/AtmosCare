from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
from contextlib import asynccontextmanager
import databases
import os

# --- Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/mydb")
database = databases.Database(DATABASE_URL)

# --- 1. Define the Lifespan Context Manager (Resolves DeprecationWarning) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup (connect to DB) and shutdown (disconnect from DB)."""
    
    # STARTUP LOGIC: Connect to the database
    try:
        await database.connect()
    except Exception as e:
        print(f"FATAL ERROR: Failed to connect to database: {e}")
    
    yield # Server is now running
    
    # SHUTDOWN LOGIC: Disconnect from the database
    await database.disconnect()

# --- 2. Create FastAPI Instance with the Lifespan ---
app = FastAPI(lifespan=lifespan)

# Enable CORS (Cleaned allow_origins)
app.add_middleware(
    CORSMiddleware,
    # Fix: Remove trailing slash from origin for standard CORS protocol
    allow_origins=["http://localhost:5173"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for response
class HighRiskRow(BaseModel):
    ZipCode: str
    LocationName: str
    VulnerabilityIndex: float
    AQI: float

# --- 3. Endpoint with Analytical SQL (Adjusted for Schema and Analysis) ---
@app.get("/api/queries/high-risk", response_model=List[HighRiskRow])
async def high_risk_query(
    aqi: float = Query(..., description="AQI threshold"),
    # Add a vulnerability threshold parameter for better analysis
    vulnerability_threshold: float = Query(0.70, description="Minimum vulnerability index (0.0 to 1.0)")
):
    if aqi < 0:
        raise HTTPException(status_code=400, detail="AQI must be >= 0")

    # Analytical Query 1: Find locations with high AQI AND high vulnerability
    # This JOINs LOCATION and WEATHER_RECORD (your true data sources)
    query = """
        SELECT
            L.zip_code AS "ZipCode",
            L.location_name AS "LocationName",
            L.vulnerability_index AS "VulnerabilityIndex",
            R.air_quality_index AS "AQI"
        FROM
            location L
        JOIN
            weather_record R ON L.zip_code = R.zip_code
        WHERE
            R.air_quality_index > :aqi
            AND L.vulnerability_index >= :vulnerability_threshold
            -- Ensure we get the latest record for real-time status:
            AND R.timestamp = (SELECT MAX(timestamp) FROM weather_record WHERE zip_code = L.zip_code) 
        ORDER BY
            R.air_quality_index DESC
        LIMIT 100
    """
    
    rows = await database.fetch_all(query=query, values={
        "aqi": aqi, 
        "vulnerability_threshold": vulnerability_threshold
    })
    
    results = [dict(row) for row in rows]
    return results