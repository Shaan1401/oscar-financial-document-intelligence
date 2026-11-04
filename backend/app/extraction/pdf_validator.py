import hashlib
import uuid
from pathlib import Path
from typing import Tuple
import pymupdf

from app.core.config import settings
from app.core.errors import InvalidPDFError, FileTooLargeError

class PDFValidator:
    """Validates PDF files for security, signature, and size compliance."""

    PDF_MAGIC_BYTES = b"%PDF-"

    @classmethod
    def validate_file_content(cls, content: bytes, original_filename: str) -> Tuple[str, str, int]:
        """
        Validates raw uploaded bytes:
          1. Verifies %PDF- magic bytes signature.
          2. Verifies file size <= MAX_UPLOAD_SIZE_BYTES.
          3. Calculates SHA-256 hash.
          4. Validates readable via PyMuPDF.
        Returns: (file_hash, safe_filename, page_count)
        """
        if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
            raise FileTooLargeError(
                f"File size ({len(content)} bytes) exceeds limit of {settings.MAX_UPLOAD_SIZE_BYTES} bytes (20 MB)"
            )

        # Check PDF signature
        if not content.startswith(cls.PDF_MAGIC_BYTES) and cls.PDF_MAGIC_BYTES not in content[:1024]:
            raise InvalidPDFError("File does not have a valid PDF header (%PDF-)")

        # Compute SHA-256 hash
        sha256_hash = hashlib.sha256(content).hexdigest()

        # Generate safe storage filename using UUID and clean extension
        safe_name = f"{uuid.uuid4().hex[:12]}_{Path(original_filename).name}"
        # Remove any path traversal or unsafe characters
        safe_name = "".join(c for c in safe_name if c.isalnum() or c in "._-")

        # Open in PyMuPDF to inspect pages and password protection
        try:
            doc = pymupdf.open(stream=content, filetype="pdf")
            if doc.is_encrypted:
                doc.close()
                raise InvalidPDFError("PDF is password-protected or encrypted. Please provide an unencrypted statement.")
            page_count = len(doc)
            if page_count == 0:
                doc.close()
                raise InvalidPDFError("PDF document has 0 pages.")
            doc.close()
        except pymupdf.FileDataError as e:
            raise InvalidPDFError(f"Corrupted or invalid PDF structure: {str(e)}")

        return sha256_hash, safe_name, page_count
