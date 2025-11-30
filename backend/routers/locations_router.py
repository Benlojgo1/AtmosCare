from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..schemas import LocationCreate, LocationUpdate, LocationRead  # adjust names if different
from ..crud import locations as locations_crud

# Assumes backend/db.py defines get_db() -> yields Session
from ..db import get_db  # <- change if your db dependency has a different name/location

router = APIRouter(prefix="/api/locations", tags=["locations"])


@router.post("/", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
def create_location(payload: LocationCreate, db: Session = Depends(get_db)):
    """
    Create a location.
    """
    try:
        loc = locations_crud.create_location(db, payload)
    except Exception as e:
        # If you'd like, catch more specific exceptions (IntegrityError, etc.)
        raise HTTPException(status_code=500, detail="Failed to create location") from e
    return loc


@router.get("/", response_model=List[LocationRead])
def list_locations(db: Session = Depends(get_db)):
    return locations_crud.get_locations(db)


@router.get("/{location_id}", response_model=LocationRead)
def get_location(location_id: int, db: Session = Depends(get_db)):
    loc = locations_crud.get_location(db, location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return loc


@router.put("/{location_id}", response_model=LocationRead)
def update_location(location_id: int, payload: LocationUpdate, db: Session = Depends(get_db)):
    loc = locations_crud.update_location(db, location_id, payload)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return loc


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(location_id: int, db: Session = Depends(get_db)):
    ok = locations_crud.delete_location(db, location_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Location not found")
    # FastAPI will return an empty body with 204
    return None