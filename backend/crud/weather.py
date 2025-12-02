from typing import List, Optional

from sqlalchemy.orm import Session

from ..models import Weather
from ..schemas import WeatherCreate, WeatherUpdate


# ---------- CREATE ----------
def create_weather_record(db: Session, data: WeatherCreate) -> Weather:
    payload = data.dict() if hasattr(data, "dict") else dict(data)
    record = Weather(**payload)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ---------- READ ----------
def get_weather_records(db: Session) -> List[Weather]:
    return db.query(Weather).all()


def get_weather_by_id(db: Session, weather_id: int) -> Optional[Weather]:
    return db.query(Weather).filter(Weather.id == weather_id).first()


def get_weather_by_location(db: Session, location_id: int) -> List[Weather]:
    return db.query(Weather).filter(Weather.location_id == location_id).all()


# ---------- UPDATE ----------
def update_weather_record(db: Session, weather_id: int, data: WeatherUpdate) -> Optional[Weather]:
    record = db.query(Weather).filter(Weather.id == weather_id).first()
    if not record:
        return None

    update_data = data.dict(exclude_unset=True) if hasattr(data, "dict") else dict(data)
    for key, value in update_data.items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record


# ---------- DELETE ----------
def delete_weather_record(db: Session, weather_id: int) -> bool:
    record = db.query(Weather).filter(Weather.id == weather_id).first()
    if not record:
        return False

    db.delete(record)
    db.commit()
    return True