from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models import Notification, NotificationStatus, NotificationType


def _to_utc_naive(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None

    # Normalize timezone-aware datetimes to UTC-naive for DB storage/comparison.
    if dt.tzinfo is not None and dt.utcoffset() is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)

    return dt


def _build_notification_content(
    notification_type: NotificationType,
    appointment_id: int,
    appointment_date: str | None = None,
) -> tuple[str, str]:
    date_text = appointment_date or "the scheduled time"

    if notification_type == NotificationType.CONFIRMATION:
        return (
            "Appointment confirmed",
            f"Your appointment #{appointment_id} is confirmed for {date_text}.",
        )

    if notification_type == NotificationType.REMINDER:
        return (
            "Appointment reminder",
            f"Reminder: your appointment #{appointment_id} is scheduled for {date_text}.",
        )

    return (
        "Appointment cancelled",
        f"Appointment #{appointment_id} scheduled for {date_text} has been cancelled.",
    )


def create_notification(
    db: Session,
    notification_type: NotificationType,
    appointment_id: int,
    patient_id: int = 0,
    doctor_id: int = 0,
    appointment_date: str | None = None,
    channel: str = "in_app",
    scheduled_for: datetime | None = None,
) -> Notification:
    title, message = _build_notification_content(notification_type, appointment_id, appointment_date)
    scheduled_for = _to_utc_naive(scheduled_for)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    sent_at = now if scheduled_for is None or scheduled_for <= now else None
    status = NotificationStatus.SENT if sent_at else NotificationStatus.PENDING

    notification = Notification(
        appointment_id=appointment_id,
        patient_id=patient_id,
        doctor_id=doctor_id,
        notification_type=notification_type,
        channel=channel,
        status=status,
        title=title,
        message=message,
        scheduled_for=scheduled_for,
        sent_at=sent_at,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def list_notifications_by_patient(db: Session, patient_id: int) -> list[Notification]:
    stmt = (
        select(Notification)
        .where(Notification.patient_id == patient_id)
        .order_by(desc(Notification.created_at))
    )
    return list(db.scalars(stmt).all())


def list_notifications_by_appointment(db: Session, appointment_id: int) -> list[Notification]:
    stmt = (
        select(Notification)
        .where(Notification.appointment_id == appointment_id)
        .order_by(desc(Notification.created_at))
    )
    return list(db.scalars(stmt).all())
