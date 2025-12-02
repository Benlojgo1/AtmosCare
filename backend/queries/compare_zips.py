from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel, constr
import databases
import os
import logging

logger = logging.getLogger("uvicorn.error")

# PostgreSQL connection string
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/mydb")

# Async database connection
database = databases.Database(DATABASE_URL)

app = FastAPI(title="AtmosCare - Compare ZIPs API")

# Enable CORS for frontend (no trailing slash on origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
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
    zip1: constr(strip_whitespace=True, min_length=3, max_length=10) = Query(
        ..., description="First ZIP code"
    ),
    zip2: constr(strip_whitespace=True, min_length=3, max_length=10) = Query(
        ..., description="Second ZIP code"
    ),
):
    """
    Compare two ZIP codes and return average temperature and humidity metrics for each.
    """
    # Basic validation handled by pydantic types above
    query = """
        SELECT "ZipCode", "AvgTemp", "AvgHumidity"
        FROM "ZipMetrics"
        WHERE ("ZipCode" = :zip1) OR ("ZipCode" = :zip2)
        ORDER BY "ZipCode"
    """

    try:
        rows = await database.fetch_all(query=query, values={"zip1": zip1, "zip2": zip2})
    except Exception as e:
        logger.exception("Database error while fetching compare ZIPs")
        raise HTTPException(status_code=500, detail="Internal server error") from e

    results = [dict(row) for row in rows]
    return results