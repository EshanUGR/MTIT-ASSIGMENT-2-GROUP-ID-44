from fastapi import FastAPI, status

from app.database import Base, engine
from app import models as _models  # noqa: F401
from app.routes import doctor_router

app = FastAPI(title="doctor-service")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "doctor-service", "status": "ok"}


app.include_router(doctor_router, prefix="/api")
