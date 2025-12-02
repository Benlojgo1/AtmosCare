from typing import List, Optional

from sqlalchemy.orm import Session

from ..models import Location
from ..schemas import LocationCreate, LocationUpdate


# ---------- CREATE ----------
def create_location(db: Session, data: LocationCreate) -> Location:
    """
    Create a new Location from a Pydantic schema.
    """
    # defensive: ensure we have a mapping (pydantic BaseModel has .dict)
    payload = data.dict() if hasattr(data, "dict") else dict(data)
    location = Location(**payload)
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


# ---------- READ ----------
def get_locations(db: Session) -> List[Location]:
    return db.query(Location).all()


def get_location(db: Session, location_id: int) -> Optional[Location]:
    return db.query(Location).filter(Location.id == location_id).first()


# ---------- UPDATE ----------
def update_location(db: Session, location_id: int, data: LocationUpdate) -> Optional[Location]:
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        return None

    update_data = data.dict(exclude_unset=True) if hasattr(data, "dict") else dict(data)
    for key, value in update_data.items():
        setattr(location, key, value)

    db.commit()
    db.refresh(location)
    return location


# ---------- DELETE ----------
def delete_location(db: Session, location_id: int) -> bool:
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        return False

    db.delete(location)
    db.commit()
    return True