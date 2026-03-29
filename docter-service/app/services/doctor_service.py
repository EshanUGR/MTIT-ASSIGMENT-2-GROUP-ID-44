"""Doctor service - Business logic for doctor operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Doctor, Availability
from app.utils.exceptions import NotFoundError


def create_doctor(db: Session, payload: dict) -> Doctor:
    """Create a new doctor."""
    doctor = Doctor(**payload)
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


def get_all_doctors(db: Session) -> list[Doctor]:
    """Get all doctors with their availability slots."""
    stmt = select(Doctor).options(selectinload(Doctor.availability_slots)).order_by(Doctor.id.asc())
    return list(db.scalars(stmt).all())


def get_doctor_by_id(db: Session, doctor_id: int) -> Doctor:
    """Get a doctor by ID."""
    stmt = (
        select(Doctor)
        .options(selectinload(Doctor.availability_slots))
        .where(Doctor.id == doctor_id)
    )
    doctor = db.scalar(stmt)
    if not doctor:
        raise NotFoundError("Doctor not found")
    return doctor


def update_doctor(db: Session, doctor_id: int, payload: dict) -> Doctor:
    """Update a doctor's information."""
    doctor = get_doctor_by_id(db, doctor_id)
    
    for field, value in payload.items():
        setattr(doctor, field, value)
    
    db.commit()
    db.refresh(doctor)
    return doctor


def delete_doctor(db: Session, doctor_id: int) -> None:
    """Delete a doctor."""
    doctor = get_doctor_by_id(db, doctor_id)
    db.delete(doctor)
    db.commit()
