from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class AccountInfoSchema(BaseModel):
    holder_name: Optional[str] = None
    account_number: Optional[str] = None
    masked_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    branch: Optional[str] = None
    currency: str = "INR"

    class Config:
        from_attributes = True

class StatementResponse(BaseModel):
    id: str
    filename: str
    file_hash: str
    bank_name: Optional[str] = None
    layout_type: str = "generic"
    pdf_type: str = "text"
    page_count: int = 1
    statement_period: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    opening_balance: Optional[float] = None
    closing_balance: Optional[float] = None
    total_debits: float = 0.0
    total_credits: float = 0.0
    expected_closing: Optional[float] = None
    variance: Optional[float] = None
    reconciliation_status: str = "PENDING"
    status: str = "UPLOADED"
    error_message: Optional[str] = None
    transaction_count: int = 0
    created_at: Optional[datetime] = None
    accounts: List[AccountInfoSchema] = []

    class Config:
        from_attributes = True

class StatementUploadResponse(BaseModel):
    id: str
    filename: str
    file_hash: str
    page_count: int
    status: str
    message: str
