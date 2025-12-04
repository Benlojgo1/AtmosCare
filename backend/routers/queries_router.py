from fastapi import APIRouter, Query
from typing import List


router = APIRouter()



@router.get("/queries/high-risk")
async def high_risk(aqi: int = Query(100, description="AQI threshold")):

    return {"query": "high-risk", "aqi": aqi, "rows": []}


@router.get("/queries/heat-outliers")
async def heat_outliers(top: int = Query(5, ge=1, le=50, description="Top N zip codes")):

    return {"query": "heat-outliers", "top": top, "rows": []}


@router.get("/queries/alerts-by-risk")
async def alerts_by_risk(riskName: str = Query(..., description="Risk name, e.g. 'Asthma'")):

    return {"query": "alerts-by-risk", "riskName": riskName, "rows": []}


@router.get("/queries/resource-allocation")
async def resource_allocation():

    return {"query": "resource-allocation", "rows": []}


@router.get("/queries/compare")
async def compare_zips(
    zip1: str = Query(..., description="First ZIP code"),
    zip2: str = Query(..., description="Second ZIP code"),
):

    return {
        "query": "compare",
        "zip1": zip1,
        "zip2": zip2,
        "rows": [],
    }
from typing import List, Dict, Any
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, constr
import logging
import inspect

from starlette.concurrency import run_in_threadpool

from ..db import database  

logger = logging.getLogger("uvicorn.error")
router = APIRouter(prefix="/api/queries", tags=["queries"])


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
