from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import databases
import os
from dotenv import load_dotenv 

# Import the necessary router objects
from .locations_router import router as locations_router
from .weather_router import router as weather_router
from .queries_router import router as queries_router

# --- INITIALIZATION BLOCK ---
# 1. Load Environment Variables from the .env file
load_dotenv() 

# 2. Retrieve individual database components
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'atmoscare')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')

# 3. Construct the DATABASE_URL string
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 4. Initialize Async database connection
database = databases.Database(DATABASE_URL)

# --- 1. Define the Lifespan Context Manager ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup (connect to DB) and shutdown (disconnect from DB)."""
    
    # STARTUP LOGIC: Connect to the database
    try:
        await database.connect()
        print("Database connected successfully.")
    except Exception as e:
        print(f"FATAL ERROR: Failed to connect to database during startup. {e}")
    
    yield
    
    # SHUTDOWN LOGIC: Disconnect from the database
    await database.disconnect()

# --- 2. Initialize the FastAPI App Instance ---
app = FastAPI(
    title="AtmosCare API",
    version="1.0.0",
    lifespan=lifespan # Manage DB connection lifecycle
)

# --- 3. Enable CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. Include Routers (Attach Endpoints) ---

# All three router modules are included and active:
app.include_router(
    locations_router, 
    prefix="/api", 
    tags=["Locations"]
)
app.include_router(
    weather_router,
    prefix="/api",
    tags=["Weather"]
)
app.include_router(
    queries_router, 
    prefix="/api", 
    tags=["Analysis"]
)

# --- 5. Basic Health Check Endpoint ---
@app.get("/")
def read_root():
    return {"status": "ok", "service": "AtmosCare API"}