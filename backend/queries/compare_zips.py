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
class CompareZipRow(BaseModel):
    ZipCode: str
    AvgTemp: float
    AvgHumidity: float

# Connect/disconnect events
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Endpoint
@app.get("/api/queries/compare", response_model=List[CompareZipRow])
async def compare_zips(
    zip1: str = Query(..., description="First ZIP code"),
    zip2: str = Query(..., description="Second ZIP code")
):
    if not zip1 or not zip2:
        raise HTTPException(status_code=400, detail="Both zip1 and zip2 are required")

    query = """
        SELECT "ZipCode", "AvgTemp", "AvgHumidity"
        FROM "ZipMetrics"
        WHERE "ZipCode" IN (:zip1, :zip2)
        ORDER BY "ZipCode"
    """
    rows = await database.fetch_all(query=query, values={"zip1": zip1, "zip2": zip2})
    results = [dict(row) for row in rows]
    return results
