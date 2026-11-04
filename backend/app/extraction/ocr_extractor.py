import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from PIL import Image

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import pytesseract
    from pytesseract import Output
except ImportError:
    pytesseract = None

from app.core.config import settings

class TesseractDetector:
    """Detects, validates, and configures Tesseract OCR on Windows and Unix systems."""

    WINDOWS_PROBE_PATHS = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe"),
    ]

    _cached_status: Optional[Dict[str, Any]] = None

    @classmethod
    def get_status(cls, refresh: bool = False) -> Dict[str, Any]:
        if cls._cached_status is not None and not refresh:
            return cls._cached_status

        exe_path: Optional[str] = None
        version: Optional[str] = None
        available = False

        # 1. Check user configured override
        if settings.TESSERACT_CMD and Path(settings.TESSERACT_CMD).is_file():
            exe_path = str(Path(settings.TESSERACT_CMD).resolve())
        
        # 2. Check system PATH
        if not exe_path:
            which_path = shutil.which("tesseract")
            if which_path:
                exe_path = which_path

        # 3. Check Windows standard directories
        if not exe_path and os.name == "nt":
            for probe in cls.WINDOWS_PROBE_PATHS:
                if os.path.isfile(probe):
                    exe_path = probe
                    break

        instructions = (
            "Tesseract OCR is not detected on this system. "
            "To enable scanned image PDF extraction, install Tesseract from "
            "https://github.com/UB-Mannheim/tesseract/wiki and restart the backend, "
            "or specify its path in .env under TESSERACT_CMD."
        )

        if exe_path and pytesseract is not None:
            try:
                pytesseract.pytesseract.tesseract_cmd = exe_path
                ver = pytesseract.get_tesseract_version()
                version = str(ver)
                available = True
                message = f"Tesseract OCR {version} detected and active at '{exe_path}'."
            except Exception as e:
                available = False
                message = f"Tesseract executable found at '{exe_path}' but execution failed: {str(e)}"
        else:
            message = "Tesseract OCR binary not found. Scanned image extraction requires Tesseract."

        cls._cached_status = {
            "available": available,
            "executable_path": exe_path,
            "version": version,
            "message": message,
            "instructions": instructions,
        }
        return cls._cached_status


class OCRPreprocessor:
    """Preprocesses document images to optimize optical character recognition accuracy."""

    @classmethod
    def preprocess(cls, pil_image: Image.Image) -> Tuple[Image.Image, float]:
        """
        Applies grayscale conversion, bilateral filtering / noise reduction,
        contrast enhancement, adaptive thresholding, and deskewing.
        Returns (preprocessed_pil_image, deskew_angle_degrees).
        """
        if cv2 is None:
            # Fallback to basic PIL grayscale and contrast enhancement
            gray = pil_image.convert("L")
            return gray, 0.0

        # Convert PIL to OpenCV format (BGR or Grayscale)
        open_cv_image = np.array(pil_image)
        if len(open_cv_image.shape) == 3:
            gray = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2GRAY)
        else:
            gray = open_cv_image

        # 1. Bilateral Filter / Noise reduction (preserves sharp character edges)
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)

        # 2. Contrast Enhancement via CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        # 3. Deskewing
        deskewed, angle = cls._deskew(enhanced)

        # 4. Adaptive Thresholding / Binarization (Otsu's thresholding)
        _, binarized = cv2.threshold(deskewed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Convert back to PIL
        result_img = Image.fromarray(binarized)
        return result_img, angle

    @classmethod
    def _deskew(cls, gray_image: np.ndarray) -> Tuple[np.ndarray, float]:
        """Estimates and corrects skew angle up to +/- 15 degrees."""
        try:
            # Invert colors so text is white
            inverted = cv2.bitwise_not(gray_image)
            coords = np.column_stack(np.where(inverted > 0))
            if len(coords) < 50:
                return gray_image, 0.0

            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            elif angle > 45:
                angle = 90 - angle
            else:
                angle = -angle

            # Only correct realistic paper feed skew (< 15 degrees)
            if abs(angle) > 15.0 or abs(angle) < 0.2:
                return gray_image, 0.0

            (h, w) = gray_image.shape[:2]
            center = (w // 2, h // 2)
            rot_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                gray_image, rot_matrix, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            return rotated, float(angle)
        except Exception:
            return gray_image, 0.0


class OCRExtractor:
    """High-level OCR extraction service with graceful fallback and coordinate preservation."""

    @classmethod
    def extract_image_text_and_blocks(cls, pil_image: Image.Image) -> Dict[str, Any]:
        """
        Executes OCR on an image. If Tesseract is unavailable, returns a clear
        diagnostic status without falsifying results.
        """
        detector_status = TesseractDetector.get_status()
        if not detector_status["available"]:
            return {
                "status": "OCR_UNAVAILABLE",
                "text": "",
                "blocks": [],
                "deskew_angle": 0.0,
                "error": detector_status["message"],
                "instructions": detector_status["instructions"],
            }

        try:
            preprocessed_img, angle = OCRPreprocessor.preprocess(pil_image)
            
            # Extract plain text
            text = pytesseract.image_to_string(preprocessed_img, config="--psm 6")

            # Extract word bounding boxes for traceability
            data = pytesseract.image_to_data(preprocessed_img, output_type=Output.DICT, config="--psm 6")
            blocks = []
            n_boxes = len(data["text"])
            for i in range(n_boxes):
                word = data["text"][i].strip()
                if word:
                    x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                    conf = float(data["conf"][i]) if "conf" in data else 0.0
                    blocks.append({
                        "text": word,
                        "bbox": f"{x},{y},{x+w},{y+h}",
                        "confidence": conf,
                    })

            return {
                "status": "SUCCESS",
                "text": text,
                "blocks": blocks,
                "deskew_angle": angle,
                "error": None,
                "instructions": None,
            }
        except Exception as e:
            return {
                "status": "FAILED",
                "text": "",
                "blocks": [],
                "deskew_angle": 0.0,
                "error": f"OCR processing encountered an error: {str(e)}",
                "instructions": None,
            }

