from typing import Optional, List
from pydantic import BaseModel

class TransactionResponse(BaseModel):
    id: int
    statement_id: str
    date: str
    description: str
    raw_description: str
    debit: float
    credit: float
    balance: Optional[float] = None
    currency: str = "INR"
    category: str
    classification_method: str
    confidence_score: Optional[float] = None
    classification_reason: Optional[str] = None
    review_status: str
    validation_status: str
    validation_warnings: Optional[str] = None
    source_page: int
    row_sequence: int
    is_duplicate: bool = False
    is_anomaly: bool = False

    class Config:
        from_attributes = True

class TransactionUpdate(BaseModel):
    category: Optional[str] = None
    review_status: Optional[str] = None
    validation_status: Optional[str] = None

class TransactionListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[TransactionResponse]
