from fastapi import FastAPI

from app.database import Base, engine
from app import models as _models  # noqa: F401
from app.routes import router as notification_router

app = FastAPI(title="notification-service")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "notification-service", "status": "ok"}


app.include_router(notification_router)
