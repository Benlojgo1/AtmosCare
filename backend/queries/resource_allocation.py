from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
import databases
import os
import logging

logger = logging.getLogger("uvicorn.error")

# PostgreSQL connection string
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/mydb"
)

# Async database connection
database = databases.Database(DATABASE_URL)

app = FastAPI(title="AtmosCare - Resource Allocation API")

# Enable CORS (no trailing slash)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response model
class AllocationRow(BaseModel):
    VulnerabilityBucket: str
    PercentUrgent: float

# Connect/disconnect events
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Endpoint
@app.get("/api/queries/resource-allocation", response_model=List[AllocationRow])
async def resource_allocation():
    """
    Returns % of urgent alerts grouped by vulnerability bucket.
    """
    query = """
        SELECT "VulnerabilityBucket", "PercentUrgent"
        FROM "ResourceAllocation"
        ORDER BY "VulnerabilityBucket"
    """

    try:
        rows = await database.fetch_all(query=query)
    except Exception as e:
        logger.exception("Database error during resource-allocation query.")
        raise HTTPException(status_code=500, detail="Internal server error") from e

    return [dict(row) for row in rows]