from fastapi import FastAPI
from . import models, database
from .routes import user_routes

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="User Service - Patient Management")

app.include_router(user_routes.router)

@app.get("/")
def root():
    return {"message": "User Service is running"}