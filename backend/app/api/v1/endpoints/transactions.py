from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.session import get_db
from app.database.models import Transaction, ReviewEvent, AuditEvent
from app.schemas.transaction import TransactionResponse, TransactionUpdate, TransactionListResponse
from app.validation.normalizer import FinancialNormalizer

router = APIRouter(prefix="/transactions", tags=["Transactions"])

def serialize_transaction(t: Transaction) -> TransactionResponse:
    debit_val = float(FinancialNormalizer.to_decimal(t.debit_minor, t.exponent))
    credit_val = float(FinancialNormalizer.to_decimal(t.credit_minor, t.exponent))
    bal_val = float(FinancialNormalizer.to_decimal(t.balance_minor, t.exponent)) if t.balance_minor is not None else None

    return TransactionResponse(
        id=t.id,
        statement_id=t.statement_id,
        date=t.date,
        description=t.description,
        raw_description=t.raw_description,
        debit=debit_val,
        credit=credit_val,
        balance=bal_val,
        currency=t.currency,
        category=t.category,
        classification_method=t.classification_method,
        confidence_score=t.confidence_score,
        classification_reason=t.classification_reason,
        review_status=t.review_status,
        validation_status=t.validation_status,
        validation_warnings=t.validation_warnings,
        source_page=t.source_page,
        row_sequence=t.row_sequence,
        is_duplicate=t.is_duplicate,
        is_anomaly=t.is_anomaly,
    )

@router.get("", response_model=TransactionListResponse)
def list_transactions(
    statement_id: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    review_status: Optional[str] = Query(None),
    validation_status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(Transaction)

    if statement_id:
        query = query.filter(Transaction.statement_id == statement_id)
    if category:
        query = query.filter(Transaction.category == category)
    if review_status:
        query = query.filter(Transaction.review_status == review_status)
    if validation_status:
        query = query.filter(Transaction.validation_status == validation_status)
    if search:
        query = query.filter(
            or_(
                Transaction.description.ilike(f"%{search}%"),
                Transaction.raw_description.ilike(f"%{search}%"),
                Transaction.date.ilike(f"%{search}%"),
            )
        )

    total = query.count()
    txns = query.order_by(Transaction.id.asc()).offset((page - 1) * page_size).limit(page_size).all()

    return TransactionListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[serialize_transaction(t) for t in txns],
    )

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return serialize_transaction(txn)

@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    update_data: TransactionUpdate,
    db: Session = Depends(get_db),
):
    txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    old_category = txn.category

    if update_data.category and update_data.category != txn.category:
        txn.category = update_data.category
        txn.classification_method = "MANUAL"
        txn.review_status = "CORRECTED"
        txn.confidence_score = 1.0
        txn.classification_reason = "Manually corrected by reviewer"

        # Log Review Event
        review_evt = ReviewEvent(
            transaction_id=txn.id,
            old_category=old_category,
            new_category=update_data.category,
            action="CORRECT",
            reason="User correction via UI",
        )
        db.add(review_evt)

        # Log Audit Event
        audit = AuditEvent(
            actor="USER",
            event_type="CORRECTION",
            statement_id=txn.statement_id,
            transaction_id=txn.id,
            details=f"Changed category from '{old_category}' to '{update_data.category}'",
        )
        db.add(audit)

    if update_data.review_status:
        txn.review_status = update_data.review_status

    if update_data.validation_status:
        txn.validation_status = update_data.validation_status

    db.commit()
    db.refresh(txn)
    return serialize_transaction(txn)
