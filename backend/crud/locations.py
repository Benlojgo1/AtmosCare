from sqlalchemy.orm import Session
from models import Location
from schemas import LocationCreate, LocationUpdate


# ---------- CREATE ----------
def create_location(db: Session, data: LocationCreate) -> Location:
    location = Location(**data.dict())
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


# ---------- READ ----------
def get_locations(db: Session):
    return db.query(Location).all()


def get_location(db: Session, location_id: int):
    return db.query(Location).filter(Location.id == location_id).first()


# ---------- UPDATE ----------
def update_location(db: Session, location_id: int, data: LocationUpdate):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        return None

    for key, value in data.dict(exclude_unset=True).items():
        setattr(location, key, value)

    db.commit()
    db.refresh(location)
    return location


# ---------- DELETE ----------
def delete_location(db: Session, location_id: int):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        return False

    db.delete(location)
    db.commit()
    return True
