from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import NotificationStatus, NotificationType


class NotificationTriggerPayload(BaseModel):
    appointment_id: int
    patient_id: int = 0
    doctor_id: int = 0
    appointment_date: str | None = None
    channel: str = "in_app"
    scheduled_for: datetime | None = None


class NotificationRead(BaseModel):
    id: int
    appointment_id: int
    patient_id: int
    doctor_id: int
    notification_type: NotificationType
    channel: str
    status: NotificationStatus
    title: str
    message: str
    scheduled_for: datetime | None
    sent_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
