"""Server entry point - Runs the FastAPI application."""

import uvicorn

from app.config import settings
from app.main import app


def run_server():
    """Start the FastAPI server."""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.PORT,
    )


if __name__ == "__main__":
    run_server()
