from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AppointmentCreate, AppointmentRead
from app.services import appointment_service

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentRead)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):

    return appointment_service.create_appointment(db, payload.model_dump())


@router.get("/by-id/{appointment_id}", response_model=AppointmentRead)
def get_appointment_by_id(appointment_id: int, db: Session = Depends(get_db)):

    appointment = appointment_service.get_appointment_by_id(db, appointment_id)

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return appointment


@router.get("/{user_id}", response_model=list[AppointmentRead])
def get_user_appointments(user_id: int, db: Session = Depends(get_db)):

    return appointment_service.get_user_appointments(db, user_id)


@router.delete("/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):

    appointment = appointment_service.delete_appointment(db, appointment_id)

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return {"message": "Appointment deleted"}