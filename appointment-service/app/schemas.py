from pydantic import BaseModel


class AppointmentCreate(BaseModel):

    patient_id: int
    doctor_id: int
    appointment_date: str


class AppointmentRead(BaseModel):

    id: int
    patient_id: int
    doctor_id: int
    appointment_date: str
    status: str

    class Config:
        from_attributes = True