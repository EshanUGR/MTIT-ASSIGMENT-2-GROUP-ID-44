from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.appointment import Appointment


def create_appointment(db: Session, payload):

    appointment = Appointment(**payload)

    db.add(appointment)

    db.commit()

    db.refresh(appointment)

    return appointment


def get_user_appointments(db: Session, user_id: int):

    stmt = select(Appointment).where(Appointment.patient_id == user_id)

    return list(db.scalars(stmt).all())


def get_appointment_by_id(db: Session, appointment_id: int):

    stmt = select(Appointment).where(Appointment.id == appointment_id)

    return db.scalar(stmt)


def delete_appointment(db: Session, appointment_id: int):

    stmt = select(Appointment).where(Appointment.id == appointment_id)

    appointment = db.scalar(stmt)

    if appointment:
        db.delete(appointment)
        db.commit()

    return appointment