"""Availability service - Business logic for availability operations."""

from sqlalchemy import and_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Availability, Doctor
from app.services.doctor_service import get_doctor_by_id
from app.utils.exceptions import ValidationError


def add_availability(
    db: Session,
    doctor_id: int,
    date,
    start_time,
    end_time,
) -> Availability:
    """Add an availability slot for a doctor."""
    # Verify doctor exists
    get_doctor_by_id(db, doctor_id)
    
    slot = Availability(
        doctor_id=doctor_id,
        date=date,
        start_time=start_time,
        end_time=end_time,
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


def get_available_doctors(
    db: Session,
    date,
    start_time=None,
    end_time=None,
) -> list[Doctor]:
    """Get doctors available on a specific date and time range."""
    if not date:
        raise ValidationError("date query parameter is required")
    
    availability_filters = [Availability.date == date]
    
    if start_time is not None:
        availability_filters.append(Availability.start_time <= start_time)
    
    if end_time is not None:
        availability_filters.append(Availability.end_time >= end_time)
    
    stmt = (
        select(Doctor)
        .join(Availability, Doctor.id == Availability.doctor_id)
        .options(selectinload(Doctor.availability_slots))
        .where(and_(*availability_filters))
        .order_by(Doctor.id.asc())
        .distinct()
    )
    
    return list(db.scalars(stmt).all())
