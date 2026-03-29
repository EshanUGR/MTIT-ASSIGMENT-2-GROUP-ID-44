from fastapi import FastAPI

from app.database import engine
from app.models import appointment
from app.routes import appointment_routes

appointment.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Appointment Service")

app.include_router(appointment_routes.router)


@app.get("/")
def root():

    return {"message": "Appointment Service Running"}