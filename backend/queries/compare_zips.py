from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
from contextlib import asynccontextmanager
import databases
import os

# --- Configuration ---
# Note: Use os.getenv('DATABASE_URL') to read from your .env file
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/mydb")
database = databases.Database(DATABASE_URL)

# --- 1. Define the Lifespan Context Manager ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup (connect to DB) and shutdown (disconnect from DB).
    """
    print("--- SERVER STARTUP: Connecting to Database ---")
    
    # STARTUP LOGIC: Connect to the database
    try:
        await database.connect()
        print("SUCCESS: Database connected.")
    except Exception as e:
        print(f"FATAL ERROR: Failed to connect to database. {e}")
    
    # Yield control to the application (server is now running)
    yield
    
    # SHUTDOWN LOGIC: Disconnect from the database
    print("--- SERVER SHUTDOWN: Disconnecting from Database ---")
    await database.disconnect()
    print("SUCCESS: Database disconnected.")

# --- 2. Create FastAPI Instance with the Lifespan ---
# This replaces the deprecated @app.on_event handlers.
app = FastAPI(lifespan=lifespan)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Note: Removed trailing slash
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for response
class CompareZipRow(BaseModel):
    ZipCode: str
    AvgTemp: float
    AvgHumidity: float

# --- 3. Endpoint with Analytical SQL ---
@app.get("/api/queries/compare", response_model=List[CompareZipRow])
async def compare_zips(
    zip1: str = Query(..., description="First ZIP code"),
    zip2: str = Query(..., description="Second ZIP code")
):
    if not zip1 or not zip2:
        raise HTTPException(status_code=400, detail="Both zip1 and zip2 are required")

    # This query dynamically calculates the averages from the raw weather data.
    query = """
        SELECT
            zip_code AS "ZipCode",
            AVG(temperature) AS "AvgTemp",
            AVG(humidity) AS "AvgHumidity"
        FROM
            weather_record
        WHERE
            zip_code IN (:zip1, :zip2)
            -- Use this line for a true analytical 7-day average:
            -- AND timestamp >= NOW() - INTERVAL '7 days' 
        GROUP BY
            zip_code
        ORDER BY
            zip_code
    """
    
    rows = await database.fetch_all(query=query, values={"zip1": zip1, "zip2": zip2})
    
    # Note: databases library returns records, which can be converted to dicts for Pydantic.
    results = [dict(row) for row in rows] 
    return results