from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel, constr
from contextlib import asynccontextmanager # <--- 1. Import this
import databases
import os
import logging

logger = logging.getLogger("uvicorn.error")

# PostgreSQL connection string
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@localhost:5432/mydb"
)

# Async database connection
database = databases.Database(DATABASE_URL)

# --- 2. Define the Lifespan Context Manager ---
# This replaces the @app.on_event("startup") and ("shutdown")
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await database.connect()
    yield
    # Shutdown logic
    await database.disconnect()

# --- 3. Pass the defined function to FastAPI ---
app = FastAPI(lifespan=lifespan)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for response
class AlertRow(BaseModel):
    ZipCode: str
    LocationName: str
    RiskName: str
    IsUrgent: bool

# Endpoint
@app.get("/api/queries/alerts-by-risk", response_model=List[AlertRow])
async def alerts_by_risk(
    riskName: constr(strip_whitespace=True, min_length=1, max_length=100)
    = Query(..., description="Name of the risk"),
):
    """
    Return up to 100 alerts for a given risk name, ordered by urgency then zipcode.
    """
    query = """
        SELECT "ZipCode", "LocationName", "RiskName", "IsUrgent"
        FROM "HealthAlerts"
        WHERE "RiskName" = :riskName
        ORDER BY "IsUrgent" DESC, "ZipCode"
        LIMIT 100
    """

    try:
        rows = await database.fetch_all(query=query, values={"riskName": riskName})
    except Exception as e:
        logger.exception("Database error while fetching alerts by risk")
        raise HTTPException(status_code=500, detail="Internal server error") from e

    results = [dict(row) for row in rows]
    return results