from fastapi import FastAPI
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

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173/"],
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
    # Adjust table/column names to match your database
    query = """
        SELECT "VulnerabilityBucket", "PercentUrgent"
        FROM "ResourceAllocation"
        ORDER BY "VulnerabilityBucket"
    """
    rows = await database.fetch_all(query=query)
    results = [dict(row) for row in rows]
    return results
