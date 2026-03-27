"""Doctor model - SQLAlchemy ORM definition."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Doctor(Base):
    """Doctor model representing a doctor in the system."""

    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    specialization: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    hospital: Mapped[str] = mapped_column(String(255), nullable=False)

    availability_slots: Mapped[list["Availability"]] = relationship(
        back_populates="doctor", cascade="all, delete-orphan"
    )
