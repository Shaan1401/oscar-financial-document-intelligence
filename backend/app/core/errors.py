"""Custom exception classes for OSCAR."""

class OscarException(Exception):
    """Base exception for OSCAR application."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class InvalidPDFError(OscarException):
    """Raised when uploaded file is not a valid PDF or fails signature check."""
    def __init__(self, message: str = "Invalid PDF file"):
        super().__init__(message, status_code=400)


class FileTooLargeError(OscarException):
    """Raised when uploaded file exceeds size limits."""
    def __init__(self, message: str = "File size exceeds allowed limit"):
        super().__init__(message, status_code=413)


class DuplicateDocumentError(OscarException):
    """Raised when identical document already exists in system."""
    def __init__(self, message: str = "Duplicate document detected", existing_id: str = ""):
        super().__init__(message, status_code=409)
        self.existing_id = existing_id


class ExtractionError(OscarException):
    """Raised when PDF text/table extraction fails."""
    def __init__(self, message: str = "Failed to extract data from document"):
        super().__init__(message, status_code=422)


class ParserNotFoundError(OscarException):
    """Raised when no compatible layout parser is identified."""
    def __init__(self, message: str = "No compatible parser profile found for document layout"):
        super().__init__(message, status_code=422)


class ReconciliationError(OscarException):
    """Raised when reconciliation calculation encounters fatal data flaws."""
    def __init__(self, message: str = "Reconciliation failed due to invalid balance data"):
        super().__init__(message, status_code=422)


class NotFoundError(OscarException):
    """Raised when requested entity is not found."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)
