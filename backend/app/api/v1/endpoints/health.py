import shutil
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health", tags=["Health"])
def health_check():
    # Detect Tesseract executable
    tesseract_found = bool(settings.TESSERACT_CMD and shutil.which(settings.TESSERACT_CMD)) or bool(shutil.which("tesseract"))
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "full_name": settings.APP_FULL_NAME,
        "version": settings.APP_VERSION,
        "tagline": settings.APP_TAGLINE,
        "ocr_available": tesseract_found,
    }
