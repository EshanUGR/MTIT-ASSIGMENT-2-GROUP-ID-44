from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Appointment(Base):

    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    patient_id: Mapped[int] = mapped_column(Integer, nullable=False)

    doctor_id: Mapped[int] = mapped_column(Integer, nullable=False)

    appointment_date: Mapped[str] = mapped_column(String(50))

    status: Mapped[str] = mapped_column(String(50), default="booked")