from typing import List, Dict, Any
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, constr
import logging
import inspect

from starlette.concurrency import run_in_threadpool

# I assume you have an async 'database' object in backend/db.py (databases.Database)
from ..db import database  # <- ensure backend/db.py exports `database` (async databases.Database)

logger = logging.getLogger("uvicorn.error")
router = APIRouter(prefix="/api/queries", tags=["queries"])


# Response models - adjust fields to match your DB schema
class AlertRow(BaseModel):
    ZipCode: str
    LocationName: str
    RiskName: str
    IsUrgent: bool


class CompareZipRow(BaseModel):
    ZipCode: str
    AvgTemp: float
    AvgHumidity: float


class HighRiskRow(BaseModel):
    ZipCode: str
    LocationName: str
    VulnerabilityIndex: float
    AQI: float


class AllocationRow(BaseModel):
    VulnerabilityBucket: str
    PercentUrgent: float


# Alerts by risk (async raw SQL using the shared async database)
@router.get("/alerts-by-risk", response_model=List[AlertRow])
async def alerts_by_risk(riskName: constr(strip_whitespace=True, min_length=1) = Query(...)):
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
    return [dict(r) for r in rows]


# Compare ZIPs
@router.get("/compare", response_model=List[CompareZipRow])
async def compare_zips(
    zip1: constr(strip_whitespace=True, min_length=3) = Query(...),
    zip2: constr(strip_whitespace=True, min_length=3) = Query(...),
):
    query = """
        SELECT "ZipCode", "AvgTemp", "AvgHumidity"
        FROM "ZipMetrics"
        WHERE ("ZipCode" = :zip1) OR ("ZipCode" = :zip2)
        ORDER BY "ZipCode"
    """
    try:
        rows = await database.fetch_all(query=query, values={"zip1": zip1, "zip2": zip2})
    except Exception as e:
        logger.exception("Database error while fetching compare zips")
        raise HTTPException(status_code=500, detail="Internal server error") from e
    return [dict(r) for r in rows]


# High-risk query
@router.get("/high-risk", response_model=List[HighRiskRow])
async def high_risk_query(aqi: float = Query(..., ge=0)):
    if aqi > 2000:
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
        logger.exception("Database error during high-risk query")
        raise HTTPException(status_code=500, detail="Internal server error") from e
    return [dict(r) for r in rows]


# Resource allocation
@router.get("/resource-allocation", response_model=List[AllocationRow])
async def resource_allocation():
    query = """
        SELECT "VulnerabilityBucket", "PercentUrgent"
        FROM "ResourceAllocation"
        ORDER BY "VulnerabilityBucket"
    """
    try:
        rows = await database.fetch_all(query=query)
    except Exception as e:
        logger.exception("Database error during resource allocation query")
        raise HTTPException(status_code=500, detail="Internal server error") from e
    return [dict(r) for r in rows]