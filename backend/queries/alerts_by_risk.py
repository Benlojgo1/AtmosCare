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
class AlertRow(BaseModel):
    ZipCode: str
    LocationName: str
    RiskName: str
    IsUrgent: bool

# Connect/disconnect events
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Endpoint
@app.get("/api/queries/alerts-by-risk", response_model=List[AlertRow])
async def alerts_by_risk(riskName: str = Query(..., description="Name of the risk")):
    if not riskName:
        raise HTTPException(status_code=400, detail="riskName is required")

    query = """
        SELECT "ZipCode", "LocationName", "RiskName", "IsUrgent"
        FROM "HealthAlerts"
        WHERE "RiskName" = :riskName
        ORDER BY "IsUrgent" DESC, "ZipCode"
        LIMIT 100
    """
    rows = await database.fetch_all(query=query, values={"riskName": riskName})
    results = [dict(row) for row in rows]
    return results
