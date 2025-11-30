from sqlalchemy.orm import Session
from models import Weather
from schemas import WeatherCreate, WeatherUpdate


# ---------- CREATE ----------
def create_weather_record(db: Session, data: WeatherCreate) -> Weather:
    w = Weather(**data.dict())
    db.add(w)
    db.commit()
    db.refresh(w)
    return w


# ---------- READ ----------
def get_weather_records(db: Session):
    return db.query(Weather).all()


def get_weather_by_id(db: Session, weather_id: int):
    return db.query(Weather).filter(Weather.id == weather_id).first()


def get_weather_by_location(db: Session, location_id: int):
    return db.query(Weather).filter(Weather.location_id == location_id).all()


# ---------- UPDATE ----------
def update_weather_record(db: Session, weather_id: int, data: WeatherUpdate):
    record = db.query(Weather).filter(Weather.id == weather_id).first()
    if not record:
        return None

    for key, value in data.dict(exclude_unset=True).items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record


# ---------- DELETE ----------
def delete_weather_record(db: Session, weather_id: int):
    record = db.query(Weather).filter(Weather.id == weather_id).first()
    if not record:
        return False

    db.delete(record)
    db.commit()
    return True
