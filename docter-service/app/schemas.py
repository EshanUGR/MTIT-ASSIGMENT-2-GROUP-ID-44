from datetime import date, time

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def to_camel(source: str) -> str:
    parts = source.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


class AvailabilityBase(BaseModel):
    date: date
    start_time: time = Field(alias="startTime")
    end_time: time = Field(alias="endTime")

    @field_validator("end_time")
    @classmethod
    def validate_time_range(cls, end_time: time, values):
        start_time = values.data.get("start_time")
        if start_time and start_time >= end_time:
            raise ValueError("startTime must be earlier than endTime")
        return end_time


class AvailabilityCreate(AvailabilityBase):
    pass


class AvailabilityRead(AvailabilityBase):
    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    id: int


class DoctorBase(BaseModel):
    name: str = Field(min_length=2)
    specialization: str = Field(min_length=2)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=15)
    hospital: str = Field(min_length=2)


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2)
    specialization: str | None = Field(default=None, min_length=2)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=7, max_length=15)
    hospital: str | None = Field(default=None, min_length=2)


class DoctorRead(DoctorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    availability_slots: list[AvailabilityRead] = Field(default_factory=list, alias="availabilitySlots")
