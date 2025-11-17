from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
import databases
import os

# PostgreSQL connection string
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/mydb")

# Async database connection
database = databases.Database(DATABASE_URL)

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173/"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for response
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

# Endpoint
@app.get("/api/queries/high-risk", response_model=List[HighRiskRow])
async def high_risk_query(aqi: float = Query(..., description="AQI threshold")):
    if aqi < 0:
        raise HTTPException(status_code=400, detail="AQI must be >= 0")

    query = """
        SELECT "ZipCode", "LocationName", "VulnerabilityIndex", "AQI"
        FROM "HeatOutliers"
        WHERE "AQI" > :aqi
        ORDER BY "AQI" DESC
        LIMIT 100
    """
    rows = await database.fetch_all(query=query, values={"aqi": aqi})
    results = [dict(row) for row in rows]
    return results
