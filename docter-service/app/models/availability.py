"""Availability model - SQLAlchemy ORM definition."""

from sqlalchemy import Date, ForeignKey, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Availability(Base):
    """Availability model representing a doctor's availability slot."""

    __tablename__ = "availability"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False,
    )
    date: Mapped[int] = mapped_column(Date, nullable=False)
    start_time: Mapped[int] = mapped_column(Time, nullable=False)
    end_time: Mapped[int] = mapped_column(Time, nullable=False)

    doctor: Mapped["Doctor"] = relationship(back_populates="availability_slots")
