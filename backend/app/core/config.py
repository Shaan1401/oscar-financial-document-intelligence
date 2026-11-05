import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BASE_DIR.parent

class Settings(BaseSettings):
    APP_NAME: str = "OSCAR"
    APP_FULL_NAME: str = "Operational Statement Classification, Analysis & Reconciliation"
    APP_DESCRIPTOR: str = "Financial Document Intelligence"
    APP_TAGLINE: str = "Every transaction deserves an explanation."
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    HOST: str = "127.0.0.1"
    PORT: int = 8000
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    # SQLite Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'oscar.db'}"

    # File storage paths
    STORAGE_DIR: Path = BASE_DIR / "storage" / "statements"
    ML_ARTIFACTS_DIR: Path = BASE_DIR / "ml_artifacts"
    SAMPLE_DATA_DIR: Path = PROJECT_ROOT / "sample_data"

    # OCR / Tesseract path (optional override)
    TESSERACT_CMD: str = ""

    # Upload constraints
    MAX_UPLOAD_SIZE_BYTES: int = 20 * 1024 * 1024  # 20 MB

    # Model threshold
    ML_CONFIDENCE_THRESHOLD: float = 0.65

    class Config:
        env_file = (str(PROJECT_ROOT / ".env"), str(BASE_DIR / ".env"), ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

# Normalize relative SQLite paths to avoid working-directory drift
if settings.DATABASE_URL in ("sqlite:///./oscar.db", "sqlite:///oscar.db", "sqlite:///./backend/oscar.db"):
    settings.DATABASE_URL = f"sqlite:///{BASE_DIR / 'oscar.db'}"

# Windows auto-detection fallback for standard Tesseract installation
if not settings.TESSERACT_CMD and os.name == "nt":
    standard_tesseract = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    if standard_tesseract.is_file():
        settings.TESSERACT_CMD = str(standard_tesseract)

# Ensure critical directories exist
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
settings.ML_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
