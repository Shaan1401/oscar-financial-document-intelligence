import os
from pathlib import Path
from fastapi import APIRouter
from app.core.config import settings
from app.extraction.ocr_extractor import TesseractDetector

router = APIRouter()

@router.get("/health", tags=["Health"])
def health_check():
    detector_status = TesseractDetector.get_status()
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "full_name": settings.APP_FULL_NAME,
        "version": settings.APP_VERSION,
        "tagline": settings.APP_TAGLINE,
        "ocr_available": detector_status["available"],
        "tesseract_version": detector_status.get("version"),
    }
