from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
from contextlib import asynccontextmanager
import databases
import os
import asyncio 

# --- Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/mydb")
database = databases.Database(DATABASE_URL)

# --- 1. Define the Lifespan Context Manager ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup (connect to DB) and shutdown (disconnect from DB).
    """
    print("--- SERVER STARTUP: Connecting to Database ---")
    
    # --- STARTUP LOGIC: Connect to the database ---
    try:
        await database.connect()
        print("SUCCESS: Database connected.")
    except Exception as e:
        print(f"FATAL ERROR: Failed to connect to database. {e}")
        # Optionally, raise the exception to prevent the server from starting
    
    # --- Yield control to the application (server is now running) ---
    yield
    
    # --- SHUTDOWN LOGIC: Disconnect from the database ---
    print("--- SERVER SHUTDOWN: Disconnecting from Database ---")
    await database.disconnect()
    print("SUCCESS: Database disconnected.")


# --- 2. Create FastAPI Instance with the Lifespan ---
app = FastAPI(lifespan=lifespan)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Note: Removed trailing slash
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for response
class AlertRow(BaseModel):
    ZipCode: str
    LocationName: str
    RiskName: str
    IsUrgent: bool

# --- 3. Endpoint (No changes needed here) ---
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

# Note: The 'app_state' dictionary is no longer needed unless you add other state management.