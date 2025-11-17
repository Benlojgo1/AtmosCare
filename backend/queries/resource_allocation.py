from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
from contextlib import asynccontextmanager # New import for modern event handling
import databases
import os

# PostgreSQL connection string
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/mydb")

# Async database connection
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
app = FastAPI(lifespan=lifespan) # Pass the lifespan manager here

# Enable CORS (Cleaned allow_origins)
app.add_middleware(
    CORSMiddleware,
    # Fix: Remove trailing slash from origin for standard CORS protocol
    allow_origins=["http://localhost:5173"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for response
class AllocationRow(BaseModel):
    VulnerabilityBucket: str
    PercentUrgent: float

# --- 3. Endpoint with Dynamic Analytical SQL ---
@app.get("/api/queries/resource-allocation", response_model=List[AllocationRow])
async def resource_allocation():
    
    # Analytical Query 4: Calculate the percentage of urgent alerts by vulnerability level.
    query = """
        WITH TotalAlerts AS (
            -- Step 1: Count total number of alerts where the location is monitored
            SELECT COUNT(RA.alert_id) AS total_alerts
            FROM risk_alert RA
            JOIN location L ON RA.zip_code = L.zip_code
        )
        SELECT
            -- Categorize locations into buckets based on their vulnerability index
            CASE
                WHEN L.vulnerability_index >= 0.75 THEN 'High'
                WHEN L.vulnerability_index >= 0.50 THEN 'Medium'
                ELSE 'Low'
            END AS "VulnerabilityBucket",
            
            -- Calculate the percentage of *Urgent* alerts coming from this bucket
            CAST(
                SUM(CASE WHEN RA.is_urgent = TRUE THEN 1 ELSE 0 END) 
                * 100.0 / NULLIF(T.total_alerts, 0)
            AS DECIMAL(5, 2)) AS "PercentUrgent"

        FROM
            risk_alert RA
        JOIN
            location L ON RA.zip_code = L.zip_code
        CROSS JOIN TotalAlerts T -- Use TotalAlerts to calculate the percentage
        GROUP BY
            "VulnerabilityBucket"
        ORDER BY
            "VulnerabilityBucket" DESC;
    """
    
    rows = await database.fetch_all(query=query)
    results = [dict(row) for row in rows]
    return results