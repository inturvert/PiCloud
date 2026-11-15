from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import APP_NAME
from app.database.connection import engine
from app.routes.files import router as files_router


app = FastAPI(
    title=APP_NAME,
    description="Self-hosted private cloud storage platform",
    version="0.1.0"
)

app.include_router(files_router)

@app.get("/")
def root():
    return {
        "application": APP_NAME,
        "message": "Welcome to PiCloud",
        "status": "running"
    }


@app.get("/api/health")
def health_check():

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as error:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(error)
        }
