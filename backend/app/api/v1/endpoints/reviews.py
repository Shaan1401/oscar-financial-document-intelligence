from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.database.session import get_db
from app.services.review_service import ReviewService
from app.core.errors import OscarException

router = APIRouter(prefix="/reviews", tags=["Human Review"])

@router.get("")
def list_review_queue(
    statement_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Retrieves flagged transactions needing human review or resolution."""
    return ReviewService.get_review_queue(db, statement_id=statement_id, limit=limit, offset=offset)

@router.post("/{transaction_id}/approve")
def approve_transaction(
    transaction_id: int,
    payload: Dict[str, Any] = Body(default={}),
    db: Session = Depends(get_db),
):
    """Approves a flagged transaction, resolving its warning/exception status."""
    try:
        reason = payload.get("reason", "Approved by human reviewer")
        txn = ReviewService.approve_transaction(db, transaction_id, reason=reason)
        return {
            "status": "APPROVED",
            "transaction_id": txn.id,
            "category": txn.category,
            "review_status": txn.review_status,
            "message": f"Transaction #{txn.id} successfully approved and resolved.",
        }
    except OscarException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to approve transaction: {str(e)}")

@router.post("/{transaction_id}/correct")
def correct_transaction(
    transaction_id: int,
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
):
    """Applies a human correction to category, description, or amounts, auditing the change."""
    try:
        txn = ReviewService.correct_transaction(
            db,
            transaction_id=transaction_id,
            new_category=payload.get("new_category"),
            new_description=payload.get("new_description"),
            new_debit=payload.get("new_debit"),
            new_credit=payload.get("new_credit"),
            reason=payload.get("reason", "Manual correction via Review Centre"),
        )
        return {
            "status": "CORRECTED",
            "transaction_id": txn.id,
            "category": txn.category,
            "description": txn.description,
            "review_status": txn.review_status,
            "message": f"Transaction #{txn.id} successfully corrected and resolved.",
        }
    except OscarException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to correct transaction: {str(e)}")

