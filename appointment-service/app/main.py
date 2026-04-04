from fastapi import FastAPI

from app.database import Base, engine
from app.models import appointment as _appointment  # noqa: F401
from app.routes.appointment_routes import router as appointment_router

app = FastAPI(title="appointment-service")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "appointment-service", "status": "ok"}


app.include_router(appointment_router)
