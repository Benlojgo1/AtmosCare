from typing import List, Optional

from sqlalchemy.orm import Session

from ..models import Alert
from ..schemas import AlertCreate, AlertUpdate


# ---------- CREATE ----------
def create_alert(db: Session, data: AlertCreate) -> Alert:
    """
    Create a new Alert from a Pydantic schema.
    """
    payload = data.dict() if hasattr(data, "dict") else dict(data)
    alert = Alert(**payload)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


# ---------- READ ----------
def get_alerts(db: Session) -> List[Alert]:
    """Return all alerts."""
    return db.query(Alert).all()


def get_alert_by_id(db: Session, alert_id: int) -> Optional[Alert]:
    """Return a single alert by its ID, or None if not found."""
    return db.query(Alert).filter(Alert.id == alert_id).first()


def get_alerts_by_location(db: Session, location_id: int) -> List[Alert]:
    """Return alerts for a specific location."""
    return db.query(Alert).filter(Alert.location_id == location_id).all()


def get_alerts_by_risk(db: Session, risk_level: str) -> List[Alert]:
    """
    Return alerts that match a given risk level.
    Assumes your Alert model has a field like `risk_level` (string/enum).
    """
    return db.query(Alert).filter(Alert.risk_level == risk_level).all()


def get_active_alerts(db: Session) -> List[Alert]:
    """
    Return alerts that are currently active.
    Assumes your Alert model has an `active` boolean column.
    """
    return db.query(Alert).filter(Alert.active.is_(True)).all()


# ---------- UPDATE ----------
def update_alert(db: Session, alert_id: int, data: AlertUpdate) -> Optional[Alert]:
    """
    Update fields on an existing alert. Returns the updated Alert or None if not found.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return None

    update_data = data.dict(exclude_unset=True) if hasattr(data, "dict") else dict(data)
    for key, value in update_data.items():
        setattr(alert, key, value)

    db.commit()
    db.refresh(alert)
    return alert


# ---------- DELETE ----------
def delete_alert(db: Session, alert_id: int) -> bool:
    """
    Delete an alert by ID. Returns True if deleted, False if alert not found.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return False

    db.delete(alert)
    db.commit()
    return True