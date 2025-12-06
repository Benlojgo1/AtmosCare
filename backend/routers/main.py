from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# 👇 import the shared database instance
from backend.utils.database import database

# Import routers
from backend.routers.locations_router import router as locations_router
from backend.routers.weather_router import router as weather_router
from backend.routers.queries_router import router as queries_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup (connect to DB) and shutdown (disconnect)."""
    try:
        await database.connect()
        print("Database connected successfully.")
    except Exception as e:
        print(f"FATAL ERROR: Failed to connect to database during startup. {e}")

    yield

    await database.disconnect()


app = FastAPI(
    title="AtmosCare API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(locations_router, prefix="/api", tags=["Locations"])
app.include_router(weather_router,   prefix="/api", tags=["Weather"])
app.include_router(queries_router,   prefix="/api", tags=["Analysis"])


@app.get("/")
def read_root():
    return {"status": "ok", "service": "AtmosCare API"}
