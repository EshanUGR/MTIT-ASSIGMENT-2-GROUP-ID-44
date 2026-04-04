from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import NotificationType
from app.schemas import NotificationRead, NotificationTriggerPayload
from app.services import (
    create_notification,
    list_notifications_by_appointment,
    list_notifications_by_patient,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/appointment/confirmation", response_model=NotificationRead, status_code=201)
def send_appointment_confirmation(
    payload: NotificationTriggerPayload,
    db: Session = Depends(get_db),
):
    return create_notification(
        db,
        notification_type=NotificationType.CONFIRMATION,
        appointment_id=payload.appointment_id,
        patient_id=payload.patient_id,
        doctor_id=payload.doctor_id,
        appointment_date=payload.appointment_date,
        channel=payload.channel,
        scheduled_for=payload.scheduled_for,
    )


@router.post("/appointment/reminder", response_model=NotificationRead, status_code=201)
def send_appointment_reminder(
    payload: NotificationTriggerPayload,
    db: Session = Depends(get_db),
):
    return create_notification(
        db,
        notification_type=NotificationType.REMINDER,
        appointment_id=payload.appointment_id,
        patient_id=payload.patient_id,
        doctor_id=payload.doctor_id,
        appointment_date=payload.appointment_date,
        channel=payload.channel,
        scheduled_for=payload.scheduled_for,
    )


@router.post("/appointment/cancellation", response_model=NotificationRead, status_code=201)
def send_appointment_cancellation(
    payload: NotificationTriggerPayload,
    db: Session = Depends(get_db),
):
    return create_notification(
        db,
        notification_type=NotificationType.CANCELLATION,
        appointment_id=payload.appointment_id,
        patient_id=payload.patient_id,
        doctor_id=payload.doctor_id,
        appointment_date=payload.appointment_date,
        channel=payload.channel,
        scheduled_for=payload.scheduled_for,
    )


@router.get("/patient/{patient_id}", response_model=list[NotificationRead])
def get_notifications_for_patient(patient_id: int, db: Session = Depends(get_db)):
    return list_notifications_by_patient(db, patient_id)


@router.get("/appointment/{appointment_id}", response_model=list[NotificationRead])
def get_notifications_for_appointment(appointment_id: int, db: Session = Depends(get_db)):
    return list_notifications_by_appointment(db, appointment_id)
