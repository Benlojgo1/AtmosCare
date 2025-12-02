from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel, Field
import databases
import os
import logging

logger = logging.getLogger("uvicorn.error")

# PostgreSQL connection string
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/mydb"
)

# Create async database connection
database = databases.Database(DATABASE_URL)

app = FastAPI(title="AtmosCare - High Risk Query API")

# Enable CORS (NO TRAILING SLASH!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response model
class HighRiskRow(BaseModel):
    ZipCode: str
    LocationName: str
    VulnerabilityIndex: float
    AQI: float

# Connect/disconnect events
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/api/queries/high-risk", response_model=List[HighRiskRow])
async def high_risk_query(
    aqi: float = Query(
        ...,
        ge=0,
        description="AQI threshold (must be >= 0)"
    )
):
    """
    Returns ZIP codes with AQI values above a specified threshold.
    """

    # Optional sanity limit for AQI values
    if aqi > 2000:  # "impossible AQI"
        raise HTTPException(status_code=400, detail="AQI threshold is unrealistically high.")

    query = """
        SELECT "ZipCode", "LocationName", "VulnerabilityIndex", "AQI"
        FROM "HeatOutliers"
        WHERE "AQI" > :aqi
        ORDER BY "AQI" DESC
        LIMIT 100
    """

    try:
        rows = await database.fetch_all(query=query, values={"aqi": aqi})
    except Exception as e:
        logger.exception("Database error during high-risk query.")
        raise HTTPException(status_code=500, detail="Internal server error") from e

    return [dict(row) for row in rows]