from datetime import date, time

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Availability, Doctor
from app.schemas import AvailabilityCreate, AvailabilityRead, DoctorCreate, DoctorRead, DoctorUpdate

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.post("", response_model=DoctorRead, status_code=status.HTTP_201_CREATED)
def create_doctor(payload: DoctorCreate, db: Session = Depends(get_db)) -> Doctor:
    doctor = Doctor(**payload.model_dump())
    db.add(doctor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Doctor with this email already exists")
    db.refresh(doctor)
    return doctor


@router.get("", response_model=list[DoctorRead])
def get_all_doctors(db: Session = Depends(get_db)) -> list[Doctor]:
    stmt = select(Doctor).options(selectinload(Doctor.availability_slots)).order_by(Doctor.id.asc())
    return list(db.scalars(stmt).all())


@router.get("/available", response_model=list[DoctorRead])
def get_available_doctors(
    date_value: date = Query(alias="date"),
    start_time: time | None = Query(default=None, alias="startTime"),
    end_time: time | None = Query(default=None, alias="endTime"),
    db: Session = Depends(get_db),
) -> list[Doctor]:
    availability_filters = [Availability.date == date_value]

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


@router.get("/{doctor_id}", response_model=DoctorRead)
def get_doctor_by_id(doctor_id: int, db: Session = Depends(get_db)) -> Doctor:
    stmt = (
        select(Doctor)
        .options(selectinload(Doctor.availability_slots))
        .where(Doctor.id == doctor_id)
    )
    doctor = db.scalar(stmt)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@router.put("/{doctor_id}", response_model=DoctorRead)
def update_doctor(doctor_id: int, payload: DoctorUpdate, db: Session = Depends(get_db)) -> Doctor:
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="At least one field is required for update")

    stmt = select(Doctor).where(Doctor.id == doctor_id)
    doctor = db.scalar(stmt)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    for field, value in changes.items():
        setattr(doctor, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Doctor with this email already exists")

    db.refresh(doctor)
    return doctor


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)) -> None:
    doctor = db.scalar(select(Doctor).where(Doctor.id == doctor_id))
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    db.delete(doctor)
    db.commit()


@router.post(
    "/{doctor_id}/availability",
    response_model=AvailabilityRead,
    status_code=status.HTTP_201_CREATED,
)
def add_availability(
    doctor_id: int,
    payload: AvailabilityCreate,
    db: Session = Depends(get_db),
) -> Availability:
    doctor = db.scalar(select(Doctor).where(Doctor.id == doctor_id))
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    slot = Availability(
        doctor_id=doctor_id,
        date=payload.date,
        start_time=payload.start_time,
        end_time=payload.end_time,
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot
