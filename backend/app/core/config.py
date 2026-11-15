import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")

APP_NAME = os.getenv("APP_NAME", "PiCloud")
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

DATABASE_URL = os.getenv("DATABASE_URL")

STORAGE_PATH = Path(
    os.getenv(
        "STORAGE_PATH",
        str(BASE_DIR.parent / "storage")
    )
)
MAX_UPLOAD_SIZE = int(
    os.getenv("MAX_UPLOAD_SIZE", 104857600)
)
